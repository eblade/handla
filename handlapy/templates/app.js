function getItemId(category, name) { return `${category}-${name}`; }

const UNCHECKED = 0;
const ARCHIVED = 1;
const CHECKED = 2;

var categories = Object();
var states = Object();
var syncs = Object();
var labels = Object();

function isVisible(itemId) {
    let state = states[itemId];
    return state === UNCHECKED || state === CHECKED;
}

function hide(itemId) {
    let item = document.getElementById(itemId);
    item.style.display = "none";
}

function show(itemId) {
    let item = document.getElementById(itemId);
    item.style.display = "";
    let label = document.getElementById(`${itemId}-label`);
    item.style.display = "";
    let state = states[itemId];
    if (state === UNCHECKED) {
        label.style.color = "#222";
        label.style.textDecoration = "none";
    } else {
        label.style.color = "#888";
        label.style.textDecoration = "strike-through";
    }
    label.innerText = labels[itemId];
}

function showForAdd(itemId) {
    let item = document.getElementById(itemId);
    item.style.display = "";
    let label = document.getElementById(`${itemId}-label`);
    label.style.textDecoration = "none";
    let state = states[itemId];
    if (state == ARCHIVED || state == CHECKED) {
        label.innerText = "+ " + labels[itemId];
        label.style.color = "#282";
    } else {
        label.innerText = "- " + labels[itemId];
        label.style.color = "#822";
    }
}

function setLabel(itemId, label) {
    let elem = document.getElementById(`${itemId}-label`);
    labels[itemId] = label;
    elem.innerText = label;
}

function setComment(itemId, comment) {
    let elem = document.getElementById(`${itemId}-comment`);
    elem.innerText = comment;
}

function setState(itemId, state) {
    states[itemId] = state;
    let label = document.getElementById(`${itemId}-label`);
    let comment = document.getElementById(`${itemId}-comment`);
    if (state == ARCHIVED) {
        label.style.textDecoration = "line-through";
        label.style.color = "#aaa";
        comment.style.color = "#888";
    } else if (state == CHECKED) {
        label.style.textDecoration = "line-through";
        label.style.color = "#888";
        comment.style.color = "#888";
    } else {  // unchecked
        label.style.textDecoration = "none";
        label.style.color = "#222";
        comment.style.color = "#000";
    }
}

function setSynced(itemId, synced) {
    syncs[itemId] = syncs;
    let container = document.getElementById(itemId);
    if (synced == 1) {
        container.classList.remove("processing");
    } else {
        container.classList.add("processing");
    }
}

function addClickHandler(itemId) {
    let elem = document.getElementById(`${itemId}-label`);
    elem.addEventListener('click', e => {
        let label = labels[itemId];
        let state = states[itemId];
        let category = categories[itemId];
        let op = `uncheck`;
        if (state == UNCHECKED) {
            op = `check`;
            setState(itemId, CHECKED);
        } else {
            setState(itemId, UNCHECKED);
        }
        setSynced(itemId, 0);

        let req = Object();
        req.operation = op;
        req.category = category;
        req.name = label;
        ws.send(JSON.stringify(req));
    });
}

function reloadItems() {
    let itemsContainer = document.getElementById('items');
    itemsContainer.innerHTML = "Loading...";
    let req = new XMLHttpRequest();
    req.open('GET', 'itm-by-cat', true);
    req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    req.onload = function() {
        itemsContainer.innerHTML = "";
        if (this.status == 200) {
            let json = JSON.parse(this.response);
            Object.values(json.categories).forEach(cat => {
                let catLabel = document.createElement("h2");
                catLabel.id = `lcat_${cat.short}`;
                catLabel.innerText = cat.name;
                itemsContainer.appendChild(catLabel);
                catContainer = document.createElement('div');
                catContainer.id = `cat_${cat.short}`;
                itemsContainer.appendChild(catContainer);
                Object.values(cat.items).forEach(itm => {
                    createItem(cat.short, itm.name, itm.state, itm.comment);
                });

            });
        filterChanged();
        }
    };
    req.send();
}

function createItem(catShort, itemName, itemState, itemComment) {
    let catContainer = document.getElementById(`cat_${catShort}`);
    let itemId = `${catShort}-${itemName}`;

    let itemContainer = document.createElement('div');
    itemContainer.classList.add('item-container');
    itemContainer.id = itemId;
    let label = document.createElement('span');
    label.classList.add('item-label');
    label.id = `${itemId}-label`;
    itemContainer.appendChild(label);
    let comment = document.createElement('span');
    comment.classList.add('item-comment');
    comment.id = `${itemId}-comment`;
    itemContainer.appendChild(comment);
    let edit = document.createElement('a');
    edit.classList.add('item-edit');
    edit.id = `${itemId}-edit`;
    edit.href = `edit-itm/${catShort}/${itemName}`;
    edit.innerText = '[ÄNDRA]';
    itemContainer.appendChild(edit);

    catContainer.appendChild(itemContainer);

    categories[itemId] = catShort;
    setState(itemId, itemState);
    setLabel(itemId, itemName);
    setComment(itemId, itemComment);
    setSynced(itemId, 1);

    addClickHandler(itemId);
}

function updateItem(item, filter) {
    if (filter) {
        let label = labels[item.id];
        if (label.toUpperCase().indexOf(filter) > -1) {
            showForAdd(item.id);
            return true;
        } else {
            hide(item.id);
            return false;
        }
    } else {
        if (isVisible(item.id)) {
            show(item.id);
            return true;
        } else {
            hide(item.id);
            return false;
        }
    }
}

function filterChanged() {
    let input = document.getElementById("search");
    let filter = input.value.toUpperCase();
    let itemList = Array.prototype.slice.call(document.getElementsByClassName("item-container"));
    let update = document.getElementById("button-update");
    let archive = document.getElementById("button-archive");
    let stopSearch = document.getElementById("button-stop-search");
    let add = document.getElementById("button-add");
    let categoryList = Array.prototype.slice.call(document.getElementsByTagName("h2"));

    if (filter) {
        update.style.display = "none";
        archive.style.display = "none";
        stopSearch.style.display = "";
        add.style.display = "";
    } else {
        update.style.display = "";
        archive.style.display = "";
        stopSearch.style.display = "none";
        add.style.display = "none";
    }

    let usedCategories = new Set();

    itemList.forEach(item => {
        if (updateItem(item, filter)) {
            usedCategories.add(`lcat_${categories[item.id]}`);
        };
    });

    categoryList.forEach(label => {
        if (usedCategories.has(label.id)) {
            label.style.display = "";
        } else {
            label.style.display = "none";
        }
    });
}

var ws;

function setUpWebSocket() {
    let protocol = location.protocol == "http:" ? "ws" : "wss";
    let host = location.host;
    let path = location.pathname.replace("index.html", "ws");
    let url = `${protocol}://${host}${path}`;
    ws = new WebSocket(url);

    ws.onopen = function() {
        console.log("Connected to websocket");
    };

    ws.onmessage = function(evt) {
        let data = evt.data;
        let obj = JSON.parse(data);
        if (obj.old !== null) {  // there is an old item that we should update
            var itemId = getItemId(obj.old.category.short, obj.old.name);
            var item = document.getElementById(itemId);
        } else if (obj.new !== null) {  // this is a new item
            createItem(obj.new.category.short, obj.new.name, obj.new.state, obj.new.comment);
            filterChanged();
            return;
        }

        if (!item) {
            console.warn(`No such item: ${obj.old.category.short}-${obj.old.name}`);
        }

        if (obj.new === null) {  // the item was deleted
            let itemId = item.id;
            item.remove();
            delete categories[itemId];
            delete states[itemId];
            delete syncs[itemId];
            delete labels[itemId];
            filterChanged();
            return;
        }

        if (obj.old.name !== obj.new.name || obj.old.category.short !== obj.new.category.short) {
            reloadItems();
            return;
        }

        setState(itemId, obj.new.state);
        setLabel(itemId, obj.new.name);
        setComment(itemId, obj.new.comment);
        setSynced(itemId, 1);

        let input = document.getElementById("search");
        let filter = input.value.toUpperCase();
        updateItem(item, filter);
    };

    ws.onclose = function(e) {
        console.log('Socket closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(setUpWebSocket, 1000);
    };

    ws.onerror = function(err) {
        console.error('Socket error: ', err.message, 'Closing socket');
        ws.close();
    };
}

function archiveItems() {
    let req = Object();
    req.operation = "archive";
    ws.send(JSON.stringify(req));
}

document.addEventListener('DOMContentLoaded', function() {
    let update = document.getElementById("button-update");
    update.addEventListener("click", e => {
        reloadItems();
    });

    let archive = document.getElementById("button-archive");
    archive.addEventListener("click", e => {
        archiveItems();
    });

    let stopSearch = document.getElementById("button-stop-search");
    stopSearch.addEventListener("click", e => {
        let input = document.getElementById("search");
        input.value = "";
        filterChanged();
    });

    let add = document.getElementById("button-add");
    add.addEventListener("click", e => {
        let input = document.getElementById("search");
        let name = input.value;
        window.location = `new-itm/first/${name}`;
    });

    reloadItems();
    setUpWebSocket();
});
