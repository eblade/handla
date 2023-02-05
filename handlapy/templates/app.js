class Item extends HTMLElement {
    get label() { return this.getAttribute('label'); }
    set label(val) { this.setAttribute('label', val); this.update(); }
    get comment() { return this.getAttribute('comment'); }
    set comment(val) { this.setAttribute('comment', val); this.update(); }
    get state() { return parseInt(this.getAttribute('state')); }
    set state(val) { this.setAttribute('state', val); this.update(); }
    get category() { return this.getAttribute('category'); }
    set category(val) { this.setAttribute('category', val); }
    get synced() { return parseInt(this.getAttribute('synced')); }
    set synced(val) { this.setAttribute('synced', val); this.update(); }

    is_unchecked() { return this.state === 0; }
    hide() { this.style.display = "none"; }
    show() {
        let label = this.shadowRoot.getElementById('label');
        this.style.display = "";
        label.style.color = "#222";
        label.innerText = this.label;
    }
    show_for_add() {
        let label = this.shadowRoot.getElementById('label');
        this.style.display = "";
        label.style.textDecoration = "none";
        if (this.state == 1) {
            label.innerText = "+ " + this.label;
            label.style.color = "#282";
        } else {
            label.innerText = "- " + this.label;
            label.style.color = "#822";
        }
    }

    constructor() { super(); }

    update() {
        let label = this.shadowRoot.getElementById('label');
        label.innerText = this.label;
        let comment = this.shadowRoot.getElementById('comment');
        comment.innerText = this.comment;
        let container = this.shadowRoot.getElementById('container');
        if (this.state == 1) {
            label.style.textDecoration = "line-through";
            label.style.color = "#888";
            comment.style.color = "#888";
        } else {
            label.style.textDecoration = "none";
            label.style.color = "#222";
            comment.style.color = "#000";
        }
        if (this.synced == 1) {
            container.classList.remove("processing");
        } else {
            container.classList.add("processing");
        }
    }

    connectedCallback() {
        let tmpl = document.getElementById('item-template');
        let shadowRoot = this.attachShadow({mode: 'open'});
        let clone = tmpl.content.cloneNode(true);
        shadowRoot.appendChild(clone);
        let label = shadowRoot.getElementById('label');
        label.innerText = this.label;
        let comment = shadowRoot.getElementById('comment');
        if (this.comment == "null") {
            this.comment = "";
        }
        comment.innerText = this.comment;
        let edit = shadowRoot.getElementById('edit');
        edit.href = `edit-itm/${this.category}/${this.label}`;

        let self = this;
        label.addEventListener('click', e => {
            let op = `uncheck?comment=${encodeURIComponent(this.comment)}`;
            if (this.is_unchecked()) {
                op = `check?comment=`;
                self.state = 1;
            } else {
                self.state = 0;
            }
            self.synced = 0;
            let req = new XMLHttpRequest();
            req.open('PUT', `itm/${this.category}/${this.label}/${op}`, true);
            req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            req.onload = function() {
                if (this.status == 200) {
                    let json = JSON.parse(this.response);
                    self.state = json.state;
                    self.synced = 1;
                }
            };
            req.send();
        });
    }
}

window.customElements.define('x-item', Item);

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
                itemsContainer.innerHTML += `<h2>${cat.name}</h2><div id="cat_${cat.short}"></div>`
                catContainer = document.getElementById(`cat_${cat.short}`);
                Object.values(cat.items).forEach(itm => {
                    catContainer.innerHTML += `<x-item label="${itm.name}" comment="${itm.comment}" state="${itm.state}" category="${cat.short}" synced="1"></x-item>`;
                });
            });
        filter_changed();
        }
    };
    req.send();
}

function filter_changed() {
    let input = document.getElementById("search");
    let filter = input.value.toUpperCase();
    let items = document.getElementsByTagName("x-item");
    let itemList = Array.prototype.slice.call(items);
    let update = document.getElementById("button-update");
    let stopSearch = document.getElementById("button-stop-search");
    let add = document.getElementById("button-add");

    if (filter) {
        update.style.display = "none";
        stopSearch.style.display = "";
        add.style.display = "";
    } else {
        update.style.display = "";
        stopSearch.style.display = "none";
        add.style.display = "none";
    }

    itemList.forEach(item => {
        if (filter) {
            if (item.label.toUpperCase().indexOf(filter) > -1) {
                item.show_for_add();
            } else {
                item.hide();
            }
        } else {
            if (item.is_unchecked()) {
                item.show();
            } else {
                item.hide();
            }
        }
    });
}

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
});
