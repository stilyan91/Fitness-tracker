
var zoomedInCard = null;

// function to handle the zooming
function zoomFunction(card) {
    // if there's a zoomed-in card and it's not the one that's clicked, zoom it out
    if (zoomedInCard && zoomedInCard != card) {
        zoomedInCard.classList.remove('zoom');
    }

    // toggle the zoom class on the clicked card
    card.classList.toggle('zoom');

    // if the clicked card is now zoomed in, update zoomedInCard; otherwise, set it to null
    if (card.classList.contains('zoom')) {
        zoomedInCard = card;
    } else {
        zoomedInCard = null;
    }
}