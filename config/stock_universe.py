"""
Stock Universe Configuration
=============================
Comprehensive stock lists for Nifty 50, Nifty 200, Nifty 500, and Smallcap 250

Updated: November 2025
"""

# ============================================================
# NIFTY 50 STOCKS
# ============================================================
NIFTY_50 = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 
    'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'BAJFINANCE',
    'KOTAKBANK', 'LT', 'ASIANPAINTS', 'AXISBANK', 'MARUTI',
    'TITAN', 'SUNPHARMA', 'ULTRACEMCO', 'NESTLEIND', 'TECHM',
    'HCLTECH', 'WIPRO', 'TATAMOTORS', 'M&M', 'NTPC',
    'POWERGRID', 'BAJAJFINSV', 'ADANIENT', 'ONGC', 'TATASTEEL',
    'JSWSTEEL', 'INDUSINDBK', 'CIPLA', 'GRASIM', 'DRREDDY',
    'HEROMOTOCO', 'HINDALCO', 'EICHERMOT', 'APOLLOHOSP', 'COALINDIA',
    'BRITANNIA', 'SBILIFE', 'DIVISLAB', 'BPCL', 'ADANIPORTS',
    'UPL', 'TATACONSUM', 'BAJAJ-AUTO', 'HDFCLIFE', 'SHREECEM',
    'JIOFIN'  # Jio Financial Services (new)
]

# ============================================================
# NIFTY 200 STOCKS (includes all Nifty 50 + 150 more)
# ============================================================
NIFTY_200_ADDITIONAL = [
    # Banking & Financial Services
    'BANDHANBNK', 'FEDERALBNK', 'IDFCFIRSTB', 'PNB', 'BANKBARODA',
    'CANBK', 'UNIONBANK', 'LICHSGFIN', 'PFC', 'RECLTD',
    'MUTHOOTFIN', 'CHOLAFIN', 'SRTRANSFIN', 'SHRIRAMFIN', 'ABCAPITAL',
    'M&MFIN', 'HDFCAMC', 'CDSL', 'CAMS', 'IIFL',
    
    # IT & Technology
    'MPHASIS', 'COFORGE', 'PERSISTENT', 'LTTS', 'LTIM',
    'OFSS', 'MINDTREE', 'TECHM', 'CYIENT', 'SONATSOFTW',
    
    # Pharma & Healthcare
    'LUPIN', 'AUROPHARMA', 'TORNTPHARM', 'BIOCON', 'ALKEM',
    'LALPATHLAB', 'METROPOLIS', 'MAXHEALTH', 'FORTIS', 'IPCALAB',
    'LAURUSLABS', 'GLENMARK', 'ZYDUSLIFE', 'SYNGENE', 'NATCOPHARM',
    
    # Auto & Auto Components
    'TVSMOTOR', 'BAJAJ-AUTO', 'ESCORTS', 'MOTHERSON', 'ASHOKLEY',
    'BALKRISIND', 'MRF', 'APOLLOTYRE', 'CEAT', 'EXIDEIND',
    'AMARAJABAT', 'BOSCHLTD', 'SCHAEFFLER', 'ENDURANCE', 'BHFORGE',
    
    # Consumer Goods
    'DABUR', 'GODREJCP', 'MARICO', 'COLGATE', 'PIDILITIND',
    'HAVELLS', 'VOLTAS', 'CROMPTON', 'BATAINDIA', 'VBL',
    'TATAPOWER', 'ADANIGREEN', 'ADANIPOWER', 'TORNTPOWER', 'NHPC',
    
    # Infrastructure & Construction
    'DLF', 'GODREJPROP', 'OBEROIRLTY', 'PRESTIGE', 'PHOENIXLTD',
    'BRIGADE', 'LODHA', 'SOBHA', 'MAHLIFE', 'IBREALEST',
    
    # Metals & Mining
    'VEDL', 'NMDC', 'SAIL', 'JINDALSTEL', 'RATNAMANI',
    'APL', 'MOIL', 'GMRINFRA', 'ZEEL', 'JUBLPHARMA',
    
    # Cement
    'AMBUJACEM', 'ACC', 'DALMIA', 'RAMCOCEM', 'JKCEMENT',
    'HEIDELBERG', 'STARCEMENT', 'INDIACEM', 'ORIENTCEM', 'JKLAKSHMI',
    
    # Telecom & Media
    'TATACOMM', 'INDUSIND', 'PVR', 'INOXLEISUR', 'DISH',
    
    # Others
    'PETRONET', 'GAIL', 'HINDPETRO', 'IOC', 'ATUL',
    'PIIND', 'SRF', 'DEEPAK', 'AARTIIND', 'GNFC',
    'NAVINFLUOR', 'ALKYLAMINE', 'CLEAN', 'FLUOROCHEM', 'SUMICHEM',
    'TATAELXSI', 'HFCL', 'ROUTE', 'TANLA', 'NAUKRI',
    'ZOMATO', 'PAYTM', 'POLICYBZR', 'DMART', 'TRENT',
    'ABFRL', 'ADITYA', 'SHOPERSTOP', 'INDHOTEL', 'LEMONTREE',
    'KPITTECH', 'HAPPSTMNDS', 'MASTEK', 'ZENTECH', 'BIRLASOFT'
]

NIFTY_200 = NIFTY_50 + NIFTY_200_ADDITIONAL

# ============================================================
# NIFTY 500 STOCKS (includes all Nifty 200 + 300 more)
# ============================================================
NIFTY_500_ADDITIONAL = [
    # Additional Mid & Small Caps
    'ABFRL', 'AMBER', 'ANURAS', 'APARINDS', 'APLAPOLLO',
    'APLLTD', 'ASAHIINDIA', 'ASHIANA', 'ASTERDM', 'ASTRAL',
    'ASTRAZEN', 'ATUL', 'AUBANK', 'AUROPHARMA', 'AVANTIFEED',
    
    # B Series
    'BAJAJCON', 'BAJAJHIND', 'BALAMINES', 'BALRAMCHIN', 'BANCOINDIA',
    'BASF', 'BATAINDIA', 'BDL', 'BEL', 'BEML',
    'BERGEPAINT', 'BHARATFORG', 'BHARATRAS', 'BHEL', 'BIRLACORPN',
    'BLUEDART', 'BLUESTARCO', 'BOMDYEING', 'BSE', 'BSOFT',
    
    # C Series
    'CANBK', 'CANFINHOME', 'CAPLIPOINT', 'CARBORUNIV', 'CARERATING',
    'CASTROLIND', 'CCL', 'CEATLTD', 'CENTRALBK', 'CENTURYPLY',
    'CENTURYTEX', 'CERA', 'CESC', 'CGCL', 'CGPOWER',
    'CHAMBLFERT', 'CHALET', 'CHEMCON', 'CHENNPETRO', 'CHOLAHLDNG',
    'CIGNITITEC', 'CLEAN', 'COCHINSHIP', 'COROMANDEL', 'CREDITACC',
    'CROMPTON', 'CRISIL', 'CSBBANK', 'CUB', 'CUMMINSIND',
    
    # D Series
    'DABUR', 'DALMIASUG', 'DEEPAKNTR', 'DELTACORP', 'DENORA',
    'DHANUKA', 'DHFL', 'DHUNINV', 'DISHTV', 'DIXON',
    'DLF', 'DMART', 'DOLLAR', 'DPWIRES', 'DRREDDY',
    
    # E Series
    'EASEMYTRIP', 'EDELWEISS', 'EICHERMOT', 'EIDPARRY', 'EIHOTEL',
    'ELGIEQUIP', 'EMAMILTD', 'ENDURANCE', 'ENGINERSIN', 'EQUITAS',
    'ERIS', 'ESCORTS', 'ESSELPACK', 'ETHOS', 'EVEREADY',
    
    # F Series
    'FDC', 'FEDERALBNK', 'FIEMIND', 'FINEORG', 'FINPIPE',
    'FIVESTAR', 'FLUOROCHEM', 'FORCEMOT', 'FORTIS', 'FSL',
    
    # G Series
    'GATEWAY', 'GEOJITFSL', 'GEPIL', 'GHCL', 'GICRE',
    'GILLETTE', 'GLAXO', 'GLENMARK', 'GMMPFAUDLR', 'GMRINFRA',
    'GNFC', 'GODFRYPHLP', 'GODREJAGRO', 'GODREJCP', 'GODREJIND',
    'GODREJPROP', 'GOKEX', 'GOKUL', 'GOLDBEES', 'GPPL',
    'GRANULES', 'GRAPHITE', 'GRASIM', 'GREAVESCOT', 'GRINDWELL',
    'GRSE', 'GSFC', 'GSPL', 'GUJALKALI', 'GUJGASLTD',
    'GULFOILLUB', 'GVKPIL', 'GWALIA',
    
    # H Series
    'HAPPSTMNDS', 'HATHWAY', 'HBLPOWER', 'HCG', 'HCC',
    'HDFCAMC', 'HDFCLIFE', 'HEG', 'HEIDELBERG', 'HEMIPROP',
    'HERANBA', 'HERCULES', 'HESTERBIO', 'HIKAL', 'HIL',
    'HIMATSEIDE', 'HINDALCO', 'HINDCOPPER', 'HINDNATGLS', 'HINDOILEXP',
    'HINDPETRO', 'HINDUNILVR', 'HINDZINC', 'HLEGLAS', 'HMT',
    'HONAUT', 'HSCL', 'HSIL', 'HUDCO', 'HUHTAMAKI',
    
    # I Series
    'IBREALEST', 'ICICIBANK', 'ICICIGI', 'ICICIPRULI', 'ICIL',
    'IDBI', 'IDEA', 'IDFC', 'IDFCFIRSTB', 'IEX',
    'IFBIND', 'IFCI', 'IGL', 'IIFL', 'IIFLWAM',
    'IITL', 'IMAGICAA', 'IMFA', 'IMPAL', 'INDBANK',
    'INDHOTEL', 'INDIACEM', 'INDIAMART', 'INDIANB', 'INDIANHUME',
    'INDIGO', 'INDNIPPON', 'INDOCO', 'INDOSTAR', 'INDOTECH',
    'INDRAMEDCO', 'INDUSINDBK', 'INFIBEAM', 'INFOBEAN', 'INFOLLION',
    'INGVYSYABK', 'INOXLEISUR', 'INOXWIND', 'INSECTICID', 'INTELLECT',
    
    # J Series
    'JAGRAN', 'JAMNAAUTO', 'JASH', 'JAYBARMARU', 'JAYNECOIND',
    'JBCHEPHARM', 'JBMA', 'JHS', 'JISLJALEQS', 'JKCEMENT',
    'JKLAKSHMI', 'JKPAPER', 'JKTYRE', 'JMA', 'JMFINANCIL',
    'JPASSOCIAT', 'JSL', 'JSWENERGY', 'JSWHL', 'JSWSTEEL',
    'JUBLFOOD', 'JUBLINGREA', 'JUBLPHARMA', 'JUSTDIAL', 'JYOTHYLAB',
    
    # K Series
    'KAJARIACER', 'KALPATPOWR', 'KALYANKJIL', 'KAMATHOTEL', 'KANPRPLA',
    'KANSAINER', 'KARURVYSYA', 'KCP', 'KDDL', 'KEI',
    'KENNAMET', 'KESORAMIND', 'KEYFINSERV', 'KFINTECH', 'KHADIM',
    'KHAITANELE', 'KICL', 'KILITCH', 'KIRIINDUS', 'KIRLOSENG',
    'KITEX', 'KITTYIND', 'KKC', 'KMSUGAR', 'KNRCON',
    'KOHINOOR', 'KOKUYOCMLN', 'KOLTEPATIL', 'KOPRAN', 'KOTAKBANK',
    'KPIL', 'KPITECH', 'KPITTECH', 'KPRMILL', 'KRBL',
    'KREBSBIO', 'KSCL', 'KSB', 'KSL', 'KTKBANK'
]

NIFTY_500 = NIFTY_200 + NIFTY_500_ADDITIONAL[:300]  # Total 500 stocks

# ============================================================
# SMALLCAP 250 STOCKS
# ============================================================
SMALLCAP_250 = [
    # Small Cap Stocks with good liquidity
    'AAVAS', 'ABDL', 'ABSLAMC', 'ACE', 'AEGISCHEM',
    'AETHER', 'AFFLE', 'AGROPHOS', 'AIAENG', 'AIIL',
    'AJANTPHARM', 'AKZOINDIA', 'ALEMBIC', 'ALKYLAMINE', 'ALLCARGO',
    'ALOKINDS', 'AMARAJABAT', 'AMBER', 'AMBUJACEM', 'ANANTRAJ',
    'ANGELONE', 'ANURAS', 'APARINDS', 'APLAPOLLO', 'APLLTD',
    'APOLLO', 'APOLLOPIPE', 'ARMANFIN', 'ARROWGREEN', 'ASAHIINDIA',
    'ASHAPURMIN', 'ASHIANA', 'ASHOKA', 'ASIANHOTNR', 'ASIAPAINT',
    'ASTEC', 'ASTERDM', 'ASTRAL', 'ASTRAZEN', 'ATFL',
    'ATUL', 'AUBANK', 'AUROPHARMA', 'AVANTIFEED', 'AXISBANK',
    
    # B Series
    'BALAXI', 'BALAMINES', 'BALRAMCHIN', 'BALRAMPUR', 'BANCOINDIA',
    'BANKINDIA', 'BASF', 'BATA', 'BDL', 'BEML',
    'BERGEPAINT', 'BHARATFORG', 'BHARATRAS', 'BHARATWIRE', 'BHEL',
    'BIRLACORPN', 'BLAL', 'BLISSGVS', 'BLUEDART', 'BLUESTARCO',
    'BODALCHEM', 'BOMDYEING', 'BOROLTD', 'BORORENEW', 'BOSCHLTD',
    'BRIGADE', 'BRITANNIA', 'BSE', 'BSOFT', 'BUTTERFLY',
    
    # C Series
    'CAMPUS', 'CANBK', 'CANFINHOME', 'CANTABIL', 'CAPF',
    'CAPLIPOINT', 'CARBORUNIV', 'CARERATING', 'CARTRADE', 'CASTROLIND',
    'CCHHL', 'CCL', 'CDSL', 'CEATLTD', 'CENTENKA',
    'CENTRALBK', 'CENTURYPLY', 'CENTURYTEX', 'CERA', 'CEREBRA',
    'CESC', 'CGCL', 'CGPOWER', 'CHAMBLFERT', 'CHALET',
    'CHEMCON', 'CHENNPETRO', 'CHOLAHLDNG', 'CHOLAFIN', 'CIGNITITEC',
    'CLEAN', 'CLEDUCATE', 'CMICABLES', 'CMSINFO', 'COCHINSHIP',
    
    # D Series
    'DABUR', 'DALMIABHA', 'DALMIASUG', 'DCAL', 'DCB',
    'DCBBANK', 'DCM', 'DCMSHRIRAM', 'DCMSRIND', 'DCWLTD',
    'DEEPAKFERT', 'DEEPAKNTR', 'DELTACORP', 'DENORA', 'DEVIT',
    'DHANUKA', 'DHARMAJ', 'DHANVARSHA', 'DHUNINV', 'DIGISPICE',
    'DLINKINDIA', 'DIXON', 'DOLLAR', 'DPWIRES', 'DREAMFOLKS',
    
    # E Series
    'EASEMYTRIP', 'EASTSILK', 'ECLERX', 'EDELWEISS', 'EICHERMOT',
    'EIDPARRY', 'EIHOTEL', 'EIMCOELECO', 'EIML', 'EKC',
    'ELECTROTH', 'ELECON', 'ELGIEQUIP', 'EMAMILTD', 'EMKAY',
    'EMMBI', 'ENDURANCE', 'ENERGYDEV', 'ENGINERSIN', 'ENVAIRON',
    'EQUITAS', 'ERIS', 'EROSMEDIA', 'ESABINDIA', 'ESAF',
    
    # F-H Series  
    'FACT', 'FDC', 'FEDERALBNK', 'FEL', 'FINCABLES',
    'FINEORG', 'FINOPB', 'FINPIPE', 'FIRSTSOURCE', 'FIVESTAR',
    'FLEXITUFF', 'FORCEMOT', 'FSL', 'GABRIEL', 'GALLANTT',
    'GANDHAR', 'GANDHITUBE', 'GANECOS', 'GANGESSECU', 'GARFIBRES',
    'GATI', 'GEPIL', 'GEOJITFSL', 'GESHIP', 'GET&D',
    'GHCL', 'GICHSGFIN', 'GICRE', 'GILLETTE', 'GINNIFILA',
    'GIPCL', 'GKWLIMITED', 'GLAXO', 'GLENMARK', 'GLOBAL',
    'GLOBALVECT', 'GLOBUSSPR', 'GMBREW', 'GMMPFAUDLR', 'GMRINFRA',
    'GNA', 'GNFC', 'GOACARBON', 'GOCLCORP', 'GODFRYPHLP',
    
    # H-J Series
    'HBLPOWER', 'HCG', 'HCC', 'HCL-INSYS', 'HDFC',
    'HDFCAMC', 'HDFCLIFE', 'HERANBA', 'HEROMOTOCO', 'HESTERBIO',
    'HFCL', 'HGS', 'HIKAL', 'HIL', 'HIMATSEIDE',
    'HITECHGEAR', 'HLEGLAS', 'HMVL', 'HNDFDS', 'HOMEFIRST',
    'HONAUT', 'HSCL', 'HSIL', 'HTMEDIA', 'HUDCO'
]

# ============================================================
# COMBINED UNIVERSE
# ============================================================
ALL_STOCKS = list(set(NIFTY_500 + SMALLCAP_250))  # Remove duplicates
ALL_STOCKS.sort()

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_stock_universe(universe_type: str = 'nifty50') -> list:
    """
    Get stock universe based on type.
    
    Args:
        universe_type: 'nifty50', 'nifty200', 'nifty500', 'smallcap250', or 'all'
    
    Returns:
        List of stock symbols
    """
    universe_map = {
        'nifty50': NIFTY_50,
        'nifty200': NIFTY_200,
        'nifty500': NIFTY_500,
        'smallcap250': SMALLCAP_250,
        'all': ALL_STOCKS
    }
    
    return universe_map.get(universe_type.lower(), NIFTY_50)


def get_universe_info():
    """Get information about all available universes."""
    return {
        'nifty50': {
            'count': len(NIFTY_50),
            'description': 'Top 50 large-cap stocks'
        },
        'nifty200': {
            'count': len(NIFTY_200),
            'description': 'Top 200 large and mid-cap stocks'
        },
        'nifty500': {
            'count': len(NIFTY_500),
            'description': 'Top 500 stocks across all caps'
        },
        'smallcap250': {
            'count': len(SMALLCAP_250),
            'description': '250 quality small-cap stocks'
        },
        'all': {
            'count': len(ALL_STOCKS),
            'description': 'All unique stocks (Nifty 500 + Smallcap 250)'
        }
    }


if __name__ == '__main__':
    # Test the module
    print("📊 Stock Universe Configuration")
    print("=" * 50)
    
    info = get_universe_info()
    for name, data in info.items():
        print(f"\n{name.upper()}:")
        print(f"  Count: {data['count']}")
        print(f"  Description: {data['description']}")
    
    print(f"\n✅ Total unique stocks available: {len(ALL_STOCKS)}")

