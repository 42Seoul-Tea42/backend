from app.db import conn
from datetime import datetime, timedelta
from app.const import MAX_SUGGEST, AGE_GAP, Gender, AREA_DISTANCE, EARTH_RADIUS, DAYS
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

    # cursor = None
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        sql = 'SELECT * FROM "User" WHERE "id" = %s;'
        cursor.execute(sql, (id, ))
        user = cursor.fetchone()

        tags, hate_tags = user['tags'], user['hate_tags']
        emoji, hate_emoji = user['emoji'], user['hate_emoji']
        longitude, latitude = user['longitude'], user['latitude']
        similar = user['similar']

        # 나이 차이 범위 AGE_GAP
        date_start = user['birthday'] - timedelta(AGE_GAP * DAYS)
        date_end = user['birthday'] + timedelta(AGE_GAP * DAYS)

        find_taste = user['gender'] | Gender.OTHER
        find_gender = Gender.ALL if user['taste'] & Gender.OTHER else user['taste']

        sql = 'SELECT * \
                FROM "User" \
                WHERE "id" != %s \
                    AND "User"."id" NOT IN ( \
                            SELECT "target_id" \
                            FROM "Block" \
                            WHERE "user_id" = %s ) \
                    AND "taste" & %s > 0 \
                    AND "gender" & %s > 0 \
                    AND "hate_tags" & %s = 0 \
                    AND "tags" & %s = 0 \
                    AND "hate_emoji" & %s = 0 \
                    AND "emoji" & %s = 0 \
                    AND "tags" & %s > 0 \
                    AND CASE WHEN %s THEN "emoji" & %s > 0 \
                            ELSE "emoji" & %s = 0 \
                        END \
                    AND "birthday" BETWEEN %s AND %s \
                    AND ( %s * acos( \
                                cos(radians("latitude")) * cos(radians(%s)) * \
                                cos(radians("longitude" - %s)) + \
                                sin(radians("latitude")) * sin(radians(%s)) \
                            ) \
                        ) < %s \
                ORDER BY CASE WHEN %s THEN "emoji" & %s \
                        END DESC, \
                        "count_fancy" / COALESCE("count_view", 1) DESC \
                LIMIT %s ;'
        
        cursor.execute(sql, (id, id,
                            find_taste, find_gender,
                            tags, hate_tags,
                            emoji, hate_emoji,
                            tags, similar, emoji, emoji,
                            date_start, date_end,
                            EARTH_RADIUS, latitude, longitude, latitude, AREA_DISTANCE,
                            similar, emoji, MAX_SUGGEST))
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
                'fame': record['count_fancy'] / record['count_view'] * 10 if record['count_view'] else 0,
                'tags': userUtils.decodeBit(record['tags']),
                'fancy': historyUtils.getFancy(id, record['id']),
            })

        cursor.close()
        return {
            'message': 'succeed',
            'data': result,
        }, 200
    
    except Exception as e:
        if cursor:
            cursor.close()
        raise e
