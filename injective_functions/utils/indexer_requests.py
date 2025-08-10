import aiohttp
from typing import Dict, Tuple
import re
import json
import logging
import asyncio


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_best_available_endpoint(is_mainnet: bool, endpoint_type: str = "lcd") -> str:
    """
    Get the best available endpoint based on connectivity test results.
    
    Args:
        is_mainnet: Whether to use mainnet or testnet
        endpoint_type: Type of endpoint ("lcd", "grpc", "tendermint_rpc")
    
    Returns:
        Best available endpoint URL
    """
    # Import here to avoid circular imports
    try:
        from network.connectivity import get_smart_endpoint, validate_endpoint_availability
    except ImportError:
        # Fallback if connectivity module not available
        logger.warning("Connectivity module not available, using default endpoints")
        return get_default_endpoint(is_mainnet, endpoint_type)
    
    try:
        environment = "mainnet" if is_mainnet else "testnet"
        logger.info(f"Getting best available {endpoint_type} endpoint for {environment}...")
        
        # 使用智能端点获取机制
        endpoint_url = get_smart_endpoint(environment, endpoint_type, force_refresh=False)
        
        # 验证端点可用性，如果不可用则自动重新测试
        is_available = await validate_endpoint_availability(environment, endpoint_type, endpoint_url, timeout=5.0)
        
        if is_available:
            logger.info(f"✅ Using validated {endpoint_type} endpoint: {endpoint_url}")
            return endpoint_url
        else:
            # 如果验证失败，强制刷新并重试
            logger.warning(f"Endpoint validation failed, forcing refresh for {environment}")
            endpoint_url = get_smart_endpoint(environment, endpoint_type, force_refresh=True)
            
            # 再次验证
            is_available = await validate_endpoint_availability(environment, endpoint_type, endpoint_url, timeout=5.0)
            if is_available:
                logger.info(f"✅ Using refreshed {endpoint_type} endpoint: {endpoint_url}")
                return endpoint_url
            else:
                logger.error(f"Failed to find available {endpoint_type} endpoint for {environment} after refresh")
                
    except Exception as e:
        logger.warning(f"Smart endpoint selection failed: {e}, using default endpoints")
    
    # Fallback to default endpoints
    default_endpoint = get_default_endpoint(is_mainnet, endpoint_type)
    logger.info(f"Using default {endpoint_type} endpoint: {default_endpoint}")
    return default_endpoint


def get_default_endpoint(is_mainnet: bool, endpoint_type: str = "lcd") -> str:
    """
    Get default endpoint URLs.
    
    Args:
        is_mainnet: Whether to use mainnet or testnet
        endpoint_type: Type of endpoint ("lcd", "grpc", "tendermint_rpc")
    
    Returns:
        Default endpoint URL
    """
    try:
        from pyinjective.core.network import Network
        # 使用pyinjective提供的端点
        net = Network.mainnet() if is_mainnet else Network.testnet()
        
        if endpoint_type == "lcd":
            return str(net.lcd_endpoint)
        elif endpoint_type == "grpc":
            return str(net.grpc_endpoint)
        elif endpoint_type == "tendermint_rpc":
            # pyinjective没有tm_endpoint，只有tm_websocket_endpoint
            # 使用可靠的旧格式端点
            if is_mainnet:
                return "https://tm.injective.network"
            else:
                return "https://testnet.tm.injective.network"
        else:
            raise ValueError(f"Unknown endpoint type: {endpoint_type}")
    except Exception:
        # 如果pyinjective失败，使用可靠的旧格式端点作为fallback
        if endpoint_type == "lcd":
            if is_mainnet:
                return "https://lcd.injective.network"
            else:
                return "https://testnet.lcd.injective.network"
        elif endpoint_type == "grpc":
            if is_mainnet:
                return "grpc.injective.network:9900"
            else:
                return "testnet.grpc.injective.network:9900"
        elif endpoint_type == "tendermint_rpc":
            if is_mainnet:
                return "https://tm.injective.network"
            else:
                return "https://testnet.tm.injective.network"
        else:
            raise ValueError(f"Unknown endpoint type: {endpoint_type}")


# This is expected to return a (kv) pair
async def fetch_decimal_denoms(is_mainnet: bool) -> Dict[str, int]:
    # Get the best available LCD endpoint
    lcd_endpoint = await get_best_available_endpoint(is_mainnet, "lcd")
    request_url = f"{lcd_endpoint}/injective/exchange/v1beta1/exchange/denom_decimals"

    logger.info(f"Fetching denoms from: {request_url}")

    try:
        # 设置超时时间为5秒，提高响应速度
        timeout_seconds = 5
        
        async def fetch_denoms():
            async with aiohttp.ClientSession() as session:
                async with session.get(request_url, timeout=aiohttp.ClientTimeout(total=timeout_seconds)) as response:
                    if response.status != 200:
                        logger.error(f"Error status code: {response.status}")
                        logger.error(f"Error response: {await response.text()}")
                        logger.warning("Returning empty denoms dict due to HTTP error")
                        return {}

                    raw_data = await response.text()
                    logger.info(f"Raw response length: {len(raw_data)}")

                    try:
                        denom_data = json.loads(raw_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {str(e)}")
                        logger.error(f"Raw response: {raw_data[:500]}...")  # Log first 500 chars
                        return {}

                    if "denom_decimals" not in denom_data:
                        logger.error("No 'denom_decimals' key in response")
                        logger.error(f"Response keys: {list(denom_data.keys())}")
                        return {}

                    denom_data = denom_data["denom_decimals"]
                    logger.info(f"Number of denoms found: {len(denom_data)}")

                    response_dic: Dict[str, int] = {}
                    for denom in denom_data:
                        try:
                            denom_name = denom["denom"]
                            decimals = int(denom["decimals"])
                            response_dic[denom_name] = decimals
                            logger.debug(f"Added denom: {denom_name} with decimals: {decimals}")
                        except (KeyError, ValueError) as e:
                            logger.warning(f"Skipping invalid denom entry: {denom}, error: {e}")
                            continue

                    logger.info(f"Successfully processed {len(response_dic)} denoms")
                    return response_dic

        # 使用超时包装整个请求
        return await asyncio.wait_for(fetch_denoms(), timeout=timeout_seconds)

    except asyncio.TimeoutError:
        logger.error(f"Request timeout after {timeout_seconds} seconds")
        return {}
    except aiohttp.ClientError as e:
        logger.error(f"Network error occurred: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error in fetch_decimal_denoms: {str(e)}")
        return {}


def extract_market_info(market_id: str) -> Tuple[str, str, str]:
    """
    Extracts base currency, quote currency and market type from market identifier.

    :param market_id: Market identifier (e.g., 'btcusdt-perp', 'btcusdt', 'eth/usdt')
    :return: Tuple of (base_currency, quote_currency, market_type)
    """
    if not market_id:
        raise ValueError("Market ID cannot be empty")

    # Convert to lowercase and remove spaces
    market = market_id.lower().strip()

    # Check for perpetual market
    is_perp = bool(re.search(r"[/-]?perp(etual)?|futures?|swap", market, re.IGNORECASE))

    # Handle concatenated format with -perp suffix (e.g., btcusdt-perp)
    if is_perp:
        # Remove the perp suffix first
        market = re.sub(
            r"[/-]?(perp(etual)?|futures?|swap)[/-]?", "", market, re.IGNORECASE
        )

    # Handle different separator cases
    if "/" in market:
        parts = market.split("/")
    elif "-" in market:
        parts = market.split("-")
    else:
        # Handle concatenated format (e.g., btcusdt)
        if market.endswith("usdt"):
            parts = [market[:-4], "usdt"]
        elif market.endswith("inj"):
            parts = [market[:-3], "inj"]
        else:
            # If no known quote currency found, assume it's all base currency
            parts = [market, "usdt"]

    # Clean and validate parts
    if len(parts) < 2:
        parts.append("usdt")  # Default quote currency

    base = re.sub(r"[^a-zA-Z0-9]", "", parts[0]).upper()
    quote = re.sub(r"[^a-zA-Z0-9]", "", parts[1]).upper()

    if not re.match(r"^[A-Z0-9]{2,10}$", base):
        raise ValueError(f"Invalid base currency format: {base}")

    if not quote:
        quote = "USDT"

    market_type = "PERP" if is_perp else "SPOT"

    return base, quote, market_type


def normalize_ticker(ticker_symbol: str) -> str:
    """
    Normalizes various ticker formats to match the API's ticker format.
    Always uses USDT as quote currency.

    :param ticker_symbol: The ticker symbol to normalize (e.g., 'btc', 'eth', 'btc-perp')
    :return: The normalized ticker symbol (e.g., 'BTC/USDT PERP')
    """
    base, quote, market_type = extract_market_info(ticker_symbol)
    market_type = f" {market_type}" if market_type == "PERP" else ""
    return f"{base}/{quote}{market_type}"


async def get_market_id(ticker_symbol: str, network_type: str = "mainnet"):
    """
    Asynchronously fetches the market_id for a given ticker symbol from the Injective API.

    :param ticker_symbol: The ticker symbol to look up (e.g., 'BTCUSDT', 'btc-usdt', 'btc')
    :return: The market_id as a string if found, else None
    """
    # Normalize the ticker symbol to match the API format
    normalized_ticker = normalize_ticker(ticker_symbol)
    request_url = ""
    # API endpoint for derivative markets
    if network_type == "mainnet":
        request_url = f"{await get_best_available_endpoint(True, 'lcd')}/injective/exchange/v1beta1/derivative/markets"
    else:
        request_url = f"{await get_best_available_endpoint(False, 'lcd')}/injective/exchange/v1beta1/derivative/markets"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url) as response:
                data = await response.json()

                # Initialize a mapping of tickers to market IDs
                ticker_to_market_id = {}

                # Check if 'markets' key exists in the response
                if "markets" in data:
                    for market_info in data["markets"]:
                        market = market_info.get("market", {})
                        ticker = market.get("ticker", "").upper()
                        market_id = market.get("market_id")

                        # Ensure market_id does not have extra quotes
                        if isinstance(market_id, str):
                            market_id = market_id.strip("'\"")

                        if ticker and market_id:
                            ticker_to_market_id[ticker] = market_id

                    # Get the market_id for the normalized ticker
                    market_id = ticker_to_market_id.get(normalized_ticker)
                    if market_id:
                        return market_id
                    else:
                        print(f"No market ID found for ticker: {normalized_ticker}")
                else:
                    print("No market data found in the response.")
        except aiohttp.ClientError as e:
            print(f"HTTP request failed: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
    return None
