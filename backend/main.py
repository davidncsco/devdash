from urllib import response
from fastapi import Request
from fastapi import FastAPI, HTTPException
from fastapi import status as statuscode
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from model import DemoQuestion, User, Car
import httpx, json
import pandas as pd
from utils import load_db

from database import (
    get_environment_vars,
    fetch_many_questions,
    create_user,
    start_the_challenge,
    start_virtual_challenge,
    fetch_leaderboard_users,
    get_car_payload,
    get_car_position,
    set_car_position,
    reset_car_in_db,
    update_user_time,
    update_virtual_user_time,
    fetch_all_cars,
)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

environment_vars = get_environment_vars()
VIRTUAL_EVENT    = environment_vars['virtual_event']        # Sandbox virtual event

# Added to create path to static files for all question images
#app.mount("/static", StaticFiles(directory="data/questions"),name="static")

@app.get("/")
async def hello_world():
    envs = get_environment_vars()
    return { 'Car simulation:' : envs['car_simulation'] }

@app.get("/questions")
async def get_many_questions():
    response = await fetch_many_questions()
    return response

# @app.get("/question/{id}}", response_model=DemoQuestion)
# async def get_question_by_id(id):
#     response = await fetch_one_question(id)
#     if response:
#         return response
#     raise HTTPException(404, f"There is no question with number {id}")

@app.post("/user",
          description="Create a new user",
          status_code=statuscode.HTTP_201_CREATED
          )
async def register_a_user(user: User):
    response = await create_user(user)
    if( response == {} ):
        raise HTTPException(403, f"user with email {user.email} have taken the challenge")
    return response

# @app.get("/user/{userid}", 
#          description="Query a user by user id",
#          response_model=User)
# async def get_user(userid: str):
#     response = await fetch_user_by_id(userid)
#     return response

# @app.get("/cars")
# async def get_all_cars():
#     response = await fetch_all_cars()
#     return response

@app.put("/start",
         response_model=Car,
         description="Signal start the challenge and return first car available for this userid")
async def start_challenge(userid: str):
    if VIRTUAL_EVENT:
        return None
    response = await start_the_challenge(userid)
    if( response ):
        return response
    raise HTTPException(404, f"Can't signal start of challenge for user {userid}")

@app.put("/startvirtual",
         response_model=User,
         description="Signal start the challenge and return current user document")
async def start_challenge(userid: str):
    user = await start_virtual_challenge(userid)
    if( user ):
        if( 'timetaken' in user):
            raise HTTPException(404, f"User already taken challenge")
        return user
    raise HTTPException(404, f"Can't signal start of virtual challenge for user {userid}")

async def send_command_to_car( url: str, payload: str ):
    if( environment_vars['car_simulation'] or payload is None ):
        return 200
    print(f'Send cmd to car {url} with payload {payload}')
    data = json.loads(payload)
    async with httpx.AsyncClient() as client:
        response = await client.post(url,json=data,timeout=20) 
        print('Sending POST cmd to car with response status code = ',response.status_code)
        if response:
            return response.status_code
        else:
            raise HTTPException(404, f"Can't send command to car with {url}")
            return 404
    return 200

@app.put("/end",
         description="Signal end of the challenge and cleanup routine")
async def end_challenge(userid: str, carid: int):
    if VIRTUAL_EVENT:
        return None
    print('end_challenge: userid=',userid,' car#',carid)
    return await update_user_time(userid,carid)


@app.put("/endvirtual",
         response_model=User,
         description="Signal end of the virtual challenge and record user time")
async def end_virtual_challenge(userid: str):
    print('end virtual challenge: userid=',userid)
    return await update_virtual_user_time(userid)
    
@app.put("/score",
        description="Actions taken after user answer a question correctly or incorrectly")
async def score_a_question(carid: int, weight: int):
    ''' If user answers the question correctly, send weight as positive number
        otherwise, send weight as negative number.
    ''' 
    if VIRTUAL_EVENT:
        return None
    current_position = await get_car_position(carid)
    new_position = current_position + weight
    if( new_position >= 0 ):
        (url,payload) = get_car_payload( carid,weight )
        print(f'Score: setting car position to {new_position} for car# {carid}')
        await set_car_position(carid,new_position)
        return await send_command_to_car( url,payload )

@app.get("/position/{carid}",
         description="Get current car position from database")
async def get_current_car_position(carid: int):
    return await get_car_position(carid)
        
@app.post("/reset/{carid}",
        description="Reset car position by car number and make it available for grab (if user quits mid-race)")
async def reset_car(carid: int):
    if VIRTUAL_EVENT:
        return 200
    current_position = await reset_car_in_db(carid)
    if( current_position == 0):
        return 200
    print('Reset car from position ',current_position)
    weight = current_position * -1
    (url,payload) =  get_car_payload( carid, weight )
    return await send_command_to_car( url, payload )


@app.put("/loaddb",
          description="Initialize question and car collections in the DB")
async def loaddb():
    return load_db()

@app.get("/loadcars")
async def load_car_data_from_db():
    return await fetch_all_cars()
    
@app.get("/rank/{email}")
async def get_user_rank(email: str):
    response = await fetch_leaderboard_users()
    response.sort(key=lambda x: x.timetaken)
    ranked = 1
    timetaken = 0
    for x in response:
        if( (x.timetaken > 0) and (x.email == email) ):
            timetaken = x.timetaken
            break
        elif( x.timetaken > 0 ):
            ranked += 1
    return { "ranked": ranked, "timetaken": timetaken }

# Migrate code from Leaderboard project here for now. This should be done in ReactJS as a
# frontend component.        
templates = Jinja2Templates(directory="data")
app.mount("/template", StaticFiles(directory="data"),name="template")

MAX_USERS_TO_DISPLAY = 15

@app.get('/leaders',
         description="Get users who completed challege with time recorded")
async def get_users(request: Request):
    if VIRTUAL_EVENT:
        return {"Hello": "I am virtual"}
    response = await fetch_leaderboard_users()
    response.sort(key=lambda x: x.timetaken)
    users_dict = []
    count = 0
    for x in response: 
        if (x.timetaken > 0) and (count < MAX_USERS_TO_DISPLAY):
            user = x.__dict__
            user.pop('start')       # Remove start optional field generated by User model
            users_dict.append(user)
            count += 1
    df = pd.DataFrame(users_dict)
    df.index = df.index + 1     # Change index starting from 1 instead of 0
    return templates.TemplateResponse('leaders.html', context={'request': request, 'data': df.to_html()})