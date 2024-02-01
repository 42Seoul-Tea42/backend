from app.db import conn
from datetime import datetime, timedelta
from app.const import MAX_SUGGEST, AGE_GAP, Gender, AREA_DISTANCE
import app.user.userUtils as userUtils
import app.history.historyUtils as historyUtils
from psycopg2.extras import DictCursor



def suggest():
    #TODO jwt에서 유저 id 가져오기
    id = 1

    # 자기자신, block user 안가져오기
    # 성적 취향이 서로 맞고
    # 싫은게 하나도 없고 (hate_tag, hate_emoji)
    # 겹치는거 많은 순(tag, emoji)
    # 유저와 같은 지역에 fame rating 높은 사람으로

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (id, ))
    user = cursor.fetchone()

    tags, hate_tags = user['tags'], user['hate_tags']
    emoji, hate_emoji = user['emoji'], user['hate_emoji']
    longitude, latitude = user['longitude'], user['latitude']

    # 나이 차이 범위 AGE_GAP
    today = datetime.today()
    date_start = today - timedelta(user['birthday'] * AGE_GAP)
    date_end = today - timedelta(user['birthday'] * AGE_GAP)

    find_taste = user['gender'] | Gender.OTHER
    find_gender = Gender.ALL if user['taste'] & Gender.OTHER else user['taste']

    sql = 'SELECT * FROM "User" \
            WHERE "id" != %s AND "id" NOT IN ( \
                                        SELECT "target_id" \
                                        FROM "Block" \
                                        WHERE "user_id" = %s ) AND \
                "taste" & %s > 0 AND "gender" & %s > 0 AND \
                "hate_tags" & %s = 0 AND "tags" & %s = 0 AND \
                "hate_emoji" & %s = 0 AND "emoji" & %s = 0 AND \
                "tags" & %s > 0 AND "emoji" & %s > 0 AND \
                earth_distance(ll_to_earth("latitude", "longitude"), ll_to_earth(%s, %s)) < %s \
                "birthday" BETWEEN %s AND %s \
            ORDER BY "count_fancy" / "count_view" DESC \
            LIMIT %s ;'
    cursor.execute(sql, (id, id,
                        find_taste, find_gender,
                        tags, hate_tags,
                        emoji, hate_emoji,
                        tags, emoji,
                        latitude, longitude, AREA_DISTANCE,
                        date_start, date_end,
                        MAX_SUGGEST))
    db_data = cursor.fetchall()
    result = []
    
    for record in db_data:

        result.append({
            'id': record['id'],
            'login_id': record['login_id'],
            'name': record['name'],
            'birthday': datetime.strftime(record['birthday'], '%Y-%m-%d'),
            'longitude': record['longitude'],
            'latitude': record['latitude'],
            'fame': record['fame_rate'],
            'tags': userUtils.decodeBit(record['tags']),
            'fancy': historyUtils.getFancy(id, record['id']),
        })

    cursor.close()

    # d = object()
    return json.dumps({
        'message': 'succeed',
        'data': result,
    })
    return json.dump(
        {
        'message': 'succeed',
        'data': result,
    })
    # return {
    #     'message': 'succeed',
    #     'data': result,
    # }, 200