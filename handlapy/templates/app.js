function getItemId(category, name) { return `${category}-${name}`; }

var categories = Object();
var states = Object();
var syncs = Object();
var labels = Object();

function isVisible(itemId) {
    let state = states[itemId];
    return state === 0 || state === 2;
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
    if (state === 0) {
        label.style.color = "#222";
        label.style.textDecoration = "none";
    } else {
        label.style.color = "#888";
        label.style.textDecoration = "strike-through";
    }
    label.innerText = labels[itemId];
}

function showForAdd() {
    let item = document.getElementById(itemId);
    item.style.display = "";
    let label = document.getElementById(`${itemId}-label`);
    label.style.textDecoration = "none";
    let state = states[itemId];
    if (state == 1 || state == 2) {
        label.innerText = "+ " + this.label;
        label.style.color = "#282";
    } else {
        label.innerText = "- " + this.label;
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
    if (state == 1) {  // archived
        label.style.textDecoration = "line-through";
        label.style.color = "#888";
        comment.style.color = "#888";
    } else if (state == 2) {  // checked
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
        if (state == 0) {
            op = `check`;
            //self.state = 2;
        } else {
            //self.state = 0;
        }
        setSynced(itemId, 0);
        //self.update();
        let req = new XMLHttpRequest();
        req.open('PUT', `itm/${category}/${label}/${op}`, true);
        req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        req.onload = function() {
            //if (this.status == 200) {
            //    let json = JSON.parse(this.response);
            //    self.state = json.state;
            //    self.synced = 1;
            //}
        };
        req.send();
    });
}

function reload_items() {
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
                itemsContainer.innerHTML += `<h2 id="lcat_${cat.short}">${cat.name}</h2><div id="cat_${cat.short}"></div>`
                catContainer = document.getElementById(`cat_${cat.short}`);
                Object.values(cat.items).forEach(itm => {
                    let itemId = `${cat.short}-${itm.name}`;
                    catContainer.innerHTML += `<div class="item-container" id="${itemId}"><span class="item-label" id="${itemId}-label"></span><span class="item-comment" id="${itemId}-comment"></span><a class="item-edit" id="${itemId}-edit" href="edit-itm/${cat.short}/${itm.name}">[ÄNDRA]</a></div>`;
                    categories[itemId] = cat.short;
                    setState(itemId, itm.state);
                    setLabel(itemId, itm.name);
                    setComment(itemId, itm.comment);
                    setSynced(itemId, 1);
                });
                Object.values(cat.items).forEach(itm => {
                    let itemId = `${cat.short}-${itm.name}`;
                    addClickHandler(itemId);
                });

            });
        filter_changed();
        }
    };
    req.send();
}

function update_item(item, filter) {
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

function filter_changed() {
    let input = document.getElementById("search");
    let filter = input.value.toUpperCase();
    let items = document.getElementsByTagName("x-item");
    let itemList = Array.prototype.slice.call(items);
    let update = document.getElementById("button-update");
    let stopSearch = document.getElementById("button-stop-search");
    let add = document.getElementById("button-add");
    let categories = document.getElementsByTagName("h2");
    let categoryList = Array.prototype.slice.call(categories);

    if (filter) {
        update.style.display = "none";
        stopSearch.style.display = "";
        add.style.display = "";
    } else {
        update.style.display = "";
        stopSearch.style.display = "none";
        add.style.display = "none";
    }

    let usedCategories = new Set();

    itemList.forEach(item => {
        if (update_item(item, filter)) {
            usedCategories.add(`lcat_${item.category}`);
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

document.addEventListener('DOMContentLoaded', function() {
    let update = document.getElementById("button-update");
    update.addEventListener("click", e => {
        reload_items();
    });

    let stopSearch = document.getElementById("button-stop-search");
    stopSearch.addEventListener("click", e => {
        let input = document.getElementById("search");
        input.value = "";
        filter_changed();
    });

    let add = document.getElementById("button-add");
    add.addEventListener("click", e => {
        let input = document.getElementById("search");
        let name = input.value;
        window.location = `new-itm/first/${name}`;
    });

    reload_items();

    if ("WebSocket" in window) {
        var ws = new WebSocket("ws://localhost:8000/ws");

        ws.onopen = function() {
            console.log("Connected to websocket");
        };

        ws.onmessage = function(evt) {
            let data = evt.data;
            let obj = JSON.parse(data);
            if (obj.old !== undefined) {  // there is an old item that we should update
                var itemId = getItemId(obj.old.category.short, obj.old.name);
                var item = document.getElementById(itemId);
            } else if (obj.new !== undefined) {  // this is a new item
                var itemId = getItemId(obj.new.category.short, obj.new.name);
                var item = document.createElement("div");
                // code goes here
            }

            if (!item) {
                console.warn(`No such item: ${obj.old.category.short}-${obj.old.name}`);
            }

            setState(itemId, obj.new.state);
            setLabel(itemId, obj.new.name);
            setComment(itemId, obj.new.comment);
            setSynced(itemId, 1);

            let input = document.getElementById("search");
            let filter = input.value.toUpperCase();
            update_item(item, filter);
        };

        ws.onclose = function() {
        };
    }
});
