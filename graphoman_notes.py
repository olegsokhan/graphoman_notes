import re
import pymongo
from pymongo import MongoClient
import asyncio
import aiohttp_mako
from aiohttp import web
from pathlib import Path

client = MongoClient('185.188.183.228', 27017)
db = client['graphoman']
notesCollection = db['notes']

@aiohttp_mako.template('notes.html')
async def listMyNotes(request):
    notes = notesCollection.find().sort('numOfWords', -1)
    notesResult = ""
    for note in notes:
        notesResult += "<p>" + note['note'] + "</p><hr/>"
    return {'notes': notesResult}


@aiohttp_mako.template('index.html')
async def addNoteRequestHandlerGET(request):
    return {}

@aiohttp_mako.template('index.html')
async def addNoteRequestHandlerPOST(request):
    post = await request.post()
    note = post.get('note')
    def get_number_of_unique_words_in_array(l):
        ulist = []
        [ulist.append(x) for x in l if x not in ulist and len(x) > 0]
        return len(ulist)
    numberOfWordsInNote = get_number_of_unique_words_in_array(
        re.sub('[^A-Za-z ]+', '', note.lower()).split(' ')
    )
    notesCollection.insert_one({'note':note, 'numOfWords':numberOfWordsInNote})
    return {}


async def init(loop):
    app = web.Application(loop=loop)
    lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                output_encoding='utf-8',
                                default_filters=['decode.utf8'])
    lookup.put_string('index.html', Path("index.html").read_text())
    lookup.put_string('notes.html', Path("notes.html").read_text())
    app.router.add_route('GET', '/', addNoteRequestHandlerGET)
    app.router.add_route('POST', '/', addNoteRequestHandlerPOST)
    app.router.add_route('GET', '/notes', listMyNotes)
    return app

loop = asyncio.get_event_loop()
app = loop.run_until_complete(init(loop))
web.run_app(app, host='185.188.183.228', port=9000)