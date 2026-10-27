#!/usr/bin/env python3
"""Модель стоимости владения (TCO). Все цены — ориентировочные публичные ставки, USD/год.
Запуск: python3 model.py            -> таблицы Markdown (base)
        python3 model.py --scenarios -> сравнение сценариев
Замените PRICES на корпоративные ставки (скидки, EDP/CUD) и перезапустите."""
import sys, copy

YEARS = [1, 2, 3, 4, 5]
BASE = dict(
    mau_end=[3.0, 10.0, 17.0, 24.0, 30.0],         # млн MAU на конец года (A-5)
    mau_avg=[1.8, 6.5, 13.5, 20.5, 27.0],          # млн MAU в среднем за год
    cells=[3, 5, 5, 6, 6],                         # число региональных ячеек
    avg_nodes_factor=[0.70, 0.85, 0.92, 0.95, 0.97],
    managed_factor=[0.80, 0.90, 0.95, 1.00, 1.00],
    telemetry_tb_end=[15, 60, 140, 245, 380],      # накопленная телеметрия, ТБ
    workouts_per_mau_year=45.6,                    # 25% DAU * 0.5 тренировок/день
    price_mult=1.0,                                # множитель цен облака
    telemetry_mult=1.0,                            # множитель объёма телеметрии
    fte_rate=140_000,                              # загруженная стоимость FTE, USD/год
    sre_fte=[10, 18, 25, 30, 35],
    dev_fte=[40, 55, 60, 65, 70],
    contingency=0.15,
    vendor_maps=False,
)
P = dict(
    node_year=2000,              # узел 8 vCPU/32 ГБ, committed
    db_base_m=4000, db_per_m=3500,      # USD/мес на ячейку: база + на 1 млн MAU ячейки
    redis_base_m=1500, redis_per_m=1200, redis_comp_m=3000,
    kafka_base_m=2000, kafka_per_m=600,
    lake_base_cell=50_000, lake_per_mau=0.015,   # USD/год на ячейку; USD/MAU/год
    obj_hot_share=0.4, obj_hot_tb_year=276, obj_cold_tb_year=48,  # $23/ТБ/мес и $4/ТБ/мес
    put_per_workout=2, put_price_per_1k=0.005, get_per_workout=10, get_price_per_1k=0.0004,
    egress_per_mau=0.0192,
    maps_selfhost_fixed=50_000, maps_selfhost_per_mau=0.01, maps_vendor_per_mau=0.18,
    notif=[15_000, 50_000, 90_000, 120_000, 150_000],
    competition_burst=[10_000, 40_000, 80_000, 110_000, 150_000],
    security=[250_000, 400_000, 550_000, 700_000, 900_000],
    licenses=[100_000, 200_000, 300_000, 400_000, 500_000],
    compliance=[300_000, 450_000, 550_000, 650_000, 800_000],
    pro_data=[200_000]*5,
    moderation_per_mau=[0.15, 0.13, 0.12, 0.115, 0.11],
    obs_share=0.08, backup_share=0.10,
)

def model(c):
    out = []
    prev_tb = 0
    for i, y in enumerate(YEARS):
        k = c['price_mult']
        cells = c['cells'][i]; m = c['mau_end'][i] / cells; avg = c['mau_avg'][i] * 1e6
        nodes_end = cells * (15 + 14 * m)
        compute = nodes_end * c['avg_nodes_factor'][i] * P['node_year'] * k
        burst = P['competition_burst'][i] * k
        mf = c['managed_factor'][i]
        db = cells * (P['db_base_m'] + P['db_per_m'] * m) * 12 * mf * k
        redis = cells * (P['redis_base_m'] + P['redis_per_m'] * m + (P['redis_comp_m'] if y >= 2 else 0)) * 12 * mf * k
        kafka = cells * (P['kafka_base_m'] + P['kafka_per_m'] * m) * 12 * mf * k
        lake = (cells * P['lake_base_cell'] + P['lake_per_mau'] * avg) * k
        tb = c['telemetry_tb_end'][i] * c['telemetry_mult']
        tb_avg = (prev_tb + tb) / 2; prev_tb = tb
        storage = tb_avg * (P['obj_hot_share'] * P['obj_hot_tb_year'] + (1 - P['obj_hot_share']) * P['obj_cold_tb_year']) * k
        wk = avg * c['workouts_per_mau_year']
        requests = (wk * P['put_per_workout'] * P['put_price_per_1k'] + wk * P['get_per_workout'] * P['get_price_per_1k']) / 1000 * k
        objects = storage + requests
        egress = avg * P['egress_per_mau'] * k
        maps = (avg * P['maps_vendor_per_mau']) if c['vendor_maps'] else (P['maps_selfhost_fixed'] + avg * P['maps_selfhost_per_mau'])
        notif = P['notif'][i]
        core = compute + burst + db + redis + kafka + lake + objects
        obs = P['obs_share'] * (compute + db + redis + kafka + lake)
        backup = P['backup_share'] * (db + objects + lake)
        infra = core + egress + maps + notif + obs + backup
        sec = P['security'][i] + P['licenses'][i]
        people = (c['sre_fte'][i] + c['dev_fte'][i]) * c['fte_rate']
        moder = avg * P['moderation_per_mau'][i]
        comp = P['compliance'][i] + P['pro_data'][i]
        sub = infra + sec + people + moder + comp
        cont = sub * c['contingency']
        total = sub + cont
        out.append(dict(year=y, mau_avg=avg, compute=compute, burst=burst, db=db, redis=redis, kafka=kafka,
            lake=lake, objects=objects, storage=storage, requests=requests, egress=egress, maps=maps, notif=notif, obs=obs, backup=backup,
            infra=infra, sec=sec, people=people, moder=moder, comp=comp, cont=cont, total=total,
            per_mau=total / avg, infra_per_mau=infra / avg, nodes=nodes_end))
    return out

def fmt(x): return f"{x/1e6:,.2f}".replace(',', ' ')
def table(rows):
    keys = [('Вычисления (K8s)', 'compute'), ('Пики соревнований (предпрогрев, CDN)', 'burst'), ('Реляционные БД', 'db'),
            ('Redis (кэш, лидерборды)', 'redis'), ('Шина событий', 'kafka'), ('Озеро/аналитика', 'lake'),
            ('Объектное хранилище (данные + запросы)', 'objects'), ('Трафик/CDN', 'egress'), ('Карты и геокодирование', 'maps'),
            ('Уведомления (e-mail/SMS)', 'notif'), ('Наблюдаемость', 'obs'), ('Резервное копирование и DR', 'backup'),
            ('**Итого инфраструктура**', 'infra'), ('Безопасность и лицензии ПО', 'sec'), ('Команды сопровождения и развития', 'people'),
            ('Модерация и поддержка пользователей', 'moder'), ('Комплаенс, аудит, данные профессионалов', 'comp'),
            ('Резерв 15%', 'cont'), ('**ИТОГО, млн USD/год**', 'total')]
    lines = ['| Статья | ' + ' | '.join(f'Год {r["year"]}' for r in rows) + ' |', '|---|' + '---|' * len(rows)]
    for name, key in keys:
        lines.append(f'| {name} | ' + ' | '.join(fmt(r[key]) for r in rows) + ' |')
    lines.append('| MAU средний, млн | ' + ' | '.join(f'{r["mau_avg"]/1e6:.1f}' for r in rows) + ' |')
    lines.append('| Всего на MAU, USD/год | ' + ' | '.join(f'{r["per_mau"]:.2f}' for r in rows) + ' |')
    lines.append('| Инфраструктура на MAU, USD/год | ' + ' | '.join(f'{r["infra_per_mau"]:.2f}' for r in rows) + ' |')
    return '\n'.join(lines)

if __name__ == '__main__':
    base = model(BASE)
    if '--scenarios' in sys.argv:
        sc = {'Базовый': {}, 'Рост ×0,5': dict(mau_end=[x*0.5 for x in BASE['mau_end']], mau_avg=[x*0.5 for x in BASE['mau_avg']]),
              'Рост ×1,5': dict(mau_end=[x*1.5 for x in BASE['mau_end']], mau_avg=[x*1.5 for x in BASE['mau_avg']]),
              'Цены облака +25%': dict(price_mult=1.25), 'Цены облака −25% (корп. скидки)': dict(price_mult=0.75),
              'Телеметрия ×2': dict(telemetry_mult=2.0), 'Карты через вендора': dict(vendor_maps=True)}
        print('| Сценарий | Год 1 | Год 2 | Год 5 | 5 лет всего |\n|---|---|---|---|---|')
        for n, o in sc.items():
            c = copy.deepcopy(BASE); c.update(o); r = model(c)
            print(f'| {n} | {fmt(r[0]["total"])} | {fmt(r[1]["total"])} | {fmt(r[4]["total"])} | {fmt(sum(x["total"] for x in r))} |')
        # стоимость при записи каждой пачки отдельным объектом
        wk = base[4]['mau_avg'] * BASE['workouts_per_mau_year']
        print('\nPUT на каждую пачку (180 пачек/тренировка), год 5, млн USD:', fmt(wk*180*P['put_price_per_1k']/1000))
    else:
        print(table(base)); print('\n5 лет всего, млн USD:', fmt(sum(r['total'] for r in base)))
        print('Узлов K8s на конец года:', [round(r['nodes']) for r in base])
