import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 10,
    duration: '30s',

    thresholds: {
        http_req_duration: ['p(80)<1000'],
    },
};

const BASE_URL = ' https://undeprecative-hung-stoney.ngrok-free.dev';

export default function () {
    let res = http.get(`${BASE_URL}/`);
    check(res, {
        'homepage status 200': (r) => r.status === 200,
    });

    res = http.post(
        `${BASE_URL}/add`,
        JSON.stringify({ item: 'k6_item', amount: 1 }),
        { headers: { 'Content-Type': 'application/json' } }
    );

    check(res, {
        'add item ok': (r) => r.status === 200,
    });

    sleep(1);
}
