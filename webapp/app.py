from flask import Flask, render_template, jsonify, request
import psutil
import os
import json
import requests
import time
import subprocess
import yaml
from pathlib import Path

app = Flask(__name__, template_folder='templates', static_folder='static')

app = Flask(__name__, template_folder='templates', static_folder='static')


def get_system_status():
    return {
        'cpu_percent': psutil.cpu_percent(interval=0.2),
        'memory': psutil.virtual_memory()._asdict(),
        'disk': psutil.disk_usage('/')._asdict(),
        'uptime': int(psutil.boot_time())
    }


def get_token_status(proxy_url: str, timeout: float = 1.0):
    data = {
        'reachable': False,
        'ok': False,
        'access_token_prefix': None,
        'expires_at': None,
        'ttl_seconds': None,
        'error': None,
    }
    try:
        r = requests.get(proxy_url, timeout=timeout)
        data['reachable'] = r.status_code == 200
        if r.status_code == 200:
            payload = r.json()
            data['access_token_prefix'] = (payload.get('access_token') or '')[:8]
            data['expires_at'] = payload.get('expires_at')
            if data['expires_at']:
                now = int(time.time())
                ttl = int(data['expires_at']) - now
                data['ttl_seconds'] = ttl
                data['ok'] = ttl > 60  # consider OK if > 60s remaining
    except Exception as e:
        data['error'] = str(e)
    return data


def get_services_status():
    proxy_demo = os.getenv('PROXY_DEMO_URL', 'http://localhost:8080/token')
    proxy_live = os.getenv('PROXY_LIVE_URL', 'http://localhost:8081/token')

    demo = get_token_status(proxy_demo)
    live = get_token_status(proxy_live)

    def status_from(ok, reachable):
        if ok:
            return 'OK'
        if reachable:
            return 'Degraded'
        return 'Down'

    services = [
        {
            'name': 'webapp',
            'kind': 'Web UI',
            'status': 'OK'
        },
        {
            'name': 'token-proxy-demo',
            'kind': 'HTTP',
            'status': status_from(demo['reachable'], demo['reachable'])
        },
        {
            'name': 'token-proxy-live',
            'kind': 'HTTP',
            'status': status_from(live['reachable'], live['reachable'])
        },
        {
            'name': 'saxo-token-daemon-demo',
            'kind': 'Daemon',
            'status': status_from(demo['ok'], demo['reachable'])
        },
        {
            'name': 'saxo-token-daemon-live',
            'kind': 'Daemon',
            'status': status_from(live['ok'], live['reachable'])
        },
    ]

    extra = {
        'demo': demo,
        'live': live,
    }
    return services, extra


def get_store_positions(store_base: str):
    try:
        r = requests.get(store_base.rstrip('/') + '/positions', timeout=2)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {"count": 0, "data": [], "error": "store_unreachable"}


def get_gateway_base(env: str | None = None) -> str:
    env = (env or os.getenv('SAXO_ENV') or 'live').lower()
    if env == 'sim':
        return os.getenv('GATEWAY_BASE', 'https://gateway.saxobank.com/sim/openapi')
    return os.getenv('GATEWAY_BASE', 'https://gateway.saxobank.com/openapi')


def get_testing_status():
    """Načíta stav testovania systému z pc/HPhome/."""
    testing_data = {
        'strategies_count': 0,
        'watchlist_count': 0,
        'last_evaluation': None,
        'total_trades': 0,
        'total_pnl': 0,
        'strategies': []
    }

    try:
        # Načítaj počet stratégií
        strategies_dir = Path('../pc/HPhome/strategies')
        if strategies_dir.exists():
            yaml_files = list(strategies_dir.glob('*.yaml'))
            testing_data['strategies_count'] = len(yaml_files)
            testing_data['strategies'] = [f.stem for f in yaml_files]

        # Načítaj watchlist
        watchlist_file = Path('../pc/HPhome/watchlist/watchlist.yaml')
        if watchlist_file.exists():
            with open(watchlist_file, 'r') as f:
                watchlist_data = yaml.safe_load(f)
                testing_data['watchlist_count'] = len(watchlist_data.get('instruments', []))

        # Načítaj posledné vyhodnotenie
        eval_file = Path('../pc/HPhome/strategy_evaluation.json')
        if eval_file.exists():
            with open(eval_file, 'r') as f:
                eval_data = json.load(f)
                testing_data['last_evaluation'] = eval_data.get('generated_at', 'N/A')
                summary = eval_data.get('summary', {})
                testing_data['total_trades'] = summary.get('total_trades', 0)
                testing_data['total_pnl'] = summary.get('net_pnl', 0)

    except Exception as e:
        testing_data['error'] = str(e)

    return testing_data


@app.route('/')
def index():
    return dashboard()


@app.route('/dashboard')
def dashboard():
    status = get_system_status()
    testing_status = get_testing_status()
    # placeholder stats
    bots = [
        {'name': 'Bot1', 'strategy': 'Trend', 'market': 'BTC', 'capital': '1000€', 'pl': '+5%', 'status': 'Running'},
        {'name': 'Bot2', 'strategy': 'MeanRev', 'market': 'EUR/USD', 'capital': '500€', 'pl': '-2%', 'status': 'Stopped'},
    ]
    # token proxy URLs from env (internal docker network names expected)
    proxy_demo = os.getenv('PROXY_DEMO_URL', 'http://localhost:8080/token')
    proxy_live = os.getenv('PROXY_LIVE_URL', 'http://localhost:8081/token')
    token_demo = None
    token_live = None
    try:
        r = requests.get(proxy_demo, timeout=1)
        if r.status_code == 200:
            token_demo = r.json()
    except Exception:
        token_demo = None
    try:
        r = requests.get(proxy_live, timeout=1)
        if r.status_code == 200:
            token_live = r.json()
    except Exception:
        token_live = None

    return render_template('index.html', status=status, bots=bots, token_demo=token_demo, token_live=token_live, testing_status=testing_status)


@app.route('/api/status')
def api_status():
    return jsonify(get_system_status())


@app.route('/bots')
def bots():
    bots_data = [
        {'name': 'Bot1', 'strategy': 'Trend', 'market': 'BTC', 'capital': '1000€', 'pl': '+5%', 'status': 'Beží'},
        {'name': 'Bot2', 'strategy': 'MeanRev', 'market': 'EUR/USD', 'capital': '500€', 'pl': '-2%', 'status': 'Stopnutý'},
    ]
    return render_template('bots.html', bots=bots_data)


@app.route('/dennik')
def dennik():
    trades = [
        {'date': '02.10.2025', 'bot': 'Bot1', 'instrument': 'BTC/USDT', 'entry': '67k', 'exit': '68k', 'pl': '+1.5%'}
    ]
    return render_template('diary.html', trades=trades)


@app.route('/strategie')
def strategie():
    strategies = [
        {'name': 'Iron Condor', 'instrument': 'SPX', 'state': 'Rolovaná', 'pl': '+3%', 'expiry': '20.10.2025'},
        {'name': 'Covered Call', 'instrument': 'TSLA', 'state': 'Otvorená', 'pl': '-1%', 'expiry': '15.11.2025'},
    ]
    return render_template('strategies.html', strategies=strategies)


@app.route('/prilezitosti')
def prilezitosti():
    opps = [
        {'time': '10:42', 'strategy': 'Breakout', 'market': 'BTC', 'proposal': 'Long @ 68,200', 'confidence': '85 %', 'state': 'Nové'}
    ]
    return render_template('opportunities.html', opportunities=opps)


@app.route('/droplet')
def droplet():
    status = get_system_status()
    services, extra = get_services_status()
    allow_control = (os.getenv('ENABLE_SERVICE_CONTROL', '0') in ('1', 'true', 'True')) or (os.getenv('ALLOW_RESTART', '0') in ('1', 'true', 'True'))
    return render_template('droplet.html', status=status, services=services, extra=extra, allow_control=allow_control)


@app.route('/reports')
def reports():
    return render_template('reports.html')


@app.route('/positions')
def positions():
    store_url = os.getenv('STORE_URL', 'http://localhost:8090')
    payload = get_store_positions(store_url)
    # derive last update timestamp if available
    last_ts = None
    try:
        if isinstance(payload, dict) and isinstance(payload.get('data'), list) and payload['data']:
            last_ts = max(int(r.get('updated_at') or 0) for r in payload['data'])
    except Exception:
        last_ts = None
    now = int(time.time())
    age = (now - last_ts) if last_ts else None
    return render_template('positions.html', payload=payload, last_updated_ts=last_ts, last_updated_age=age)


@app.route('/settings')
def settings():
    allow_control = (os.getenv('ENABLE_SERVICE_CONTROL', '0') in ('1', 'true', 'True')) or (os.getenv('ALLOW_RESTART', '0') in ('1', 'true', 'True'))
    return render_template('settings.html', allow_control=allow_control)


@app.route('/api/services')
def api_services():
    services, extra = get_services_status()
    return jsonify({'services': services, 'details': extra})


@app.route('/api/restart/<service>', methods=['POST'])
def api_restart(service: str):
    allowed = {
        'token-proxy-demo', 'token-proxy-live', 'saxo-token-daemon-demo', 'saxo-token-daemon-live'
    }
    if (os.getenv('ENABLE_SERVICE_CONTROL', '0') not in ('1', 'true', 'True')) and (os.getenv('ALLOW_RESTART', '0') not in ('1', 'true', 'True')):
        return jsonify({'ok': False, 'error': 'Service control disabled'}), 403
    if service not in allowed:
        return jsonify({'ok': False, 'error': 'Service not allowed'}), 400

    # Try docker compose restart; requires that the webapp runs where docker compose is available
    compose_file = os.getenv('COMPOSE_FILE', '')  # optional
    cmd = ['docker', 'compose']
    if compose_file:
        cmd += ['-f', compose_file]
    cmd += ['restart', service]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        if proc.returncode == 0:
            return jsonify({'ok': True, 'message': proc.stdout.decode('utf-8')})
        return jsonify({'ok': False, 'error': proc.stderr.decode('utf-8') or 'restart failed'}), 500
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/ingest-now', methods=['POST'])
def api_ingest_now():
    # Guard (can be disabled via env)
    if os.getenv('ALLOW_INGEST_NOW', '1') not in ('1', 'true', 'True', 'yes', 'on'):
        return jsonify({'ok': False, 'error': 'Ingest disabled'}), 403

    proxy_url = os.getenv('PROXY_LIVE_URL', 'http://token-proxy-live-reader:8080/token')
    store_url = os.getenv('STORE_URL', 'http://positions-store:8090')
    gw = get_gateway_base(os.getenv('SAXO_ENV', 'live'))

    try:
        # 1) get token
        tr = requests.get(proxy_url, timeout=5)
        if tr.status_code != 200:
            return jsonify({'ok': False, 'step': 'token', 'status': tr.status_code, 'error': tr.text[:200]}), 502
        token = (tr.json() or {}).get('access_token')
        if not token:
            return jsonify({'ok': False, 'step': 'token', 'error': 'No access_token from proxy'}), 502

        # 2) fetch positions
        url = f"{gw}/port/v1/positions/me"
        params = {"FieldGroups": "PositionBase,DisplayAndFormat,PositionView"}
        hr = requests.get(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}, params=params, timeout=20)
        if hr.status_code == 401:
            return jsonify({'ok': False, 'step': 'openapi', 'status': 401, 'error': 'Unauthorized. Check scopes and LIVE token.'}), 401
        if hr.status_code >= 400:
            return jsonify({'ok': False, 'step': 'openapi', 'status': hr.status_code, 'error': hr.text[:200]}), 502
        data = hr.json()

        # 3) post to store
        ir = requests.post(store_url.rstrip('/') + '/ingest', headers={"Content-Type": "application/json"}, data=json.dumps(data), timeout=10)
        ok = (ir.status_code // 100) == 2
        return jsonify({'ok': ok, 'store_status': ir.status_code, 'store_resp': (ir.text or '')[:200], 'positions_count': len((data or {}).get('Data') or (data or {}).get('Positions') or [])})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=True)
