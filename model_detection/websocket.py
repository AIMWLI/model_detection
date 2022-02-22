import json


async def websocket_application(scope, receive, send):
    while True:
        event = await receive()
        print(event['type'])
        if event['type'] == 'websocket.connect':
            await send({
                'type': 'websocket.accept'
            })

        if event['type'] == 'websocket.disconnect':
            break

        if event['type'] == 'websocket.receive':
            json_data = json.loads(event['text'])
            if json_data['img'] is not None:
                await send({
                    'type': 'websocket.send',
                    'text': 'result:' + "abcd"
                })
            if 'result' in json_data:
                await send({
                    'type': 'websocket.send',
                    'text': 'result' + json_data['result'] + ' and  true is ' + str(json_data['true'])
                })

            if event['text'] == 'ping':
                join = "OCR BALABALA"
                await send({
                    'type': 'websocket.send',
                    'text': join
                })
