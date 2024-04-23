from fastapi import FastAPI, status
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel


class Vote(BaseModel):
    id: type(int)
    answer: str


class Poll(BaseModel):
    id: type(int)
    name: str
    vote_id_counter: int = 1
    votes: {int} = {}


poll_id_counter = 2
polls = {
    1: Poll(id=1, name="Czy lubisz herbatę?")
}

app = FastAPI()


@app.get("/poll")
def get_polls():
    return {"polls": polls}


@app.post("/poll")
def create_poll(poll: Poll):
    new_id = poll_id_counter
    polls[new_id] += 1
    poll = Poll(id=new_id, name=poll.name)
    polls[new_id] = poll
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=poll)


@app.get("/poll/{id}")
def get_poll_by_id(id: int):
    try:
        return polls[id]
    except KeyError:
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND)


@app.put("/poll/{id}")
def update_poll(id: int, poll: Poll):
    try:
        polls.update({id: poll})
    except KeyError:
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND)


@app.delete("/poll/{id}")
def delete_poll(id: int):
    try:
        del polls[id]
    except KeyError:
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/poll/{id}/vote")
def cast_vote(id: int, vote: Vote):
    try:
        vote_id = polls[id].vote_id_counter
        polls[id].vote_id_counter += 1
        vote = Vote(id=vote_id, answer=vote.answer)
        polls[id].votes[vote_id] = vote
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=vote)
    except KeyError:
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND)


@app.get("/poll/{poll_id}/vote/{vote_id}")
def get_vote_by_id(poll_id: int, vote_id: int):
    try:
        vote = polls[poll_id].votes[vote_id]
        return vote
    except KeyError:
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND)


@app.put("/poll/{poll_id}/vote/{vote_id}")
def update_vote(poll_id: int, vote_id: int, vote: Vote):
    try:
        polls[poll_id].votes.update({vote_id: vote})
    except KeyError:
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND)


@app.delete("/poll/{poll_id}/vote/{vote_id}")
def delete_vote(poll_id: int, vote_id: int):
    try:
        del polls[poll_id].votes[vote_id]
    except KeyError:
        return HTMLResponse(status_code=status.HTTP_404_NOT_FOUND)
