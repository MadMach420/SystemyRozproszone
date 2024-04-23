const { rankBoard, rankDescription } = require('phe')
const express = require('express')
const app = express()
const port = 3000
const path = require('path');

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '/main.html'));
})


app.get('/new_webpage', async (req, res) => {
    let decks = req.query.decks;
    let count = req.query.count;
    
    const response = await get_response_webpage(decks, count);
    res.status(response[0]).send(response[1]);
})


async function get_response_webpage(decks, count) {
    let webpage = "<html><body>"
    
    const quote_response = await get_quote();
    if (quote_response[0] == 200){
        webpage += quote_response[1];
    } else {
        return quote_response
    }
    
    const cards_response = await get_cards(decks, count);
    if (cards_response[0] == 200){
        webpage += cards_response[1];
    } else {
        return cards_response
    }
    
    webpage += "</body></html>";

    return [200, webpage];
}


async function get_cards(decks, count) {
    if (decks < 1 || 10 < decks  || count < 5 || 7 < count) {
        return [400, "Wrong Params"]
    }

    const res = await fetch("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count="+decks, {
        method: "GET",
        headers: {
            "Accept": "application/json"
        }
    }).then(res => {
        return res.json();
    }).catch(err => {
        return [502, "Bad Gateway"]
    });
    if (Array.isArray(res)) return res;

    const deck_id = res.deck_id;

    const data = await fetch(`https://deckofcardsapi.com/api/deck/${deck_id}/draw/?count=${count}`, {
        method: "GET",
        headers: {
            "Accept": "application/json"
        },
    }).then(
        res => res.json()
    ).catch(err => {
        return [502, "Bad Gateway"]
    });
    if (Array.isArray(res)) return res;

    const remaining = data.remaining;
    const cards = data.cards;
    let cards_html = `<p>${remaining} cards remaining</p>`;
    for (let card of cards) {
        cards_html += `<img src="${card.images.png}" alt=${card.code}>`;
    }
    cards_html += `<p>${evaluate_hand(cards)}</p>`;

    return [200, cards_html];
}


function evaluate_hand(cards) {
    const hand = cards.map(card => card.code[0] + card.code[1].toLowerCase());
    const rank = rankDescription[rankBoard(hand.join(" "))];
    return `Your hand is a ${rank}`;
}


function get_quote() {
    return fetch("https://stoic.tekloon.net/stoic-quote")
        .then(res => res.json())
        .then(data => [200, `<h2>${data.quote}</h2><h3>~${data.author}</h3>`])
        .catch(err => [502, "Bad Gateway"]);
}


app.listen(port, () => {
    console.log(`App listening on port ${port}`)
})