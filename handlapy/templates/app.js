class Item extends HTMLElement {
    get label() { return this.getAttribute('label'); }
    set label(val) { this.setAttribute('label', val); this.update(); }
    get comment() { return this.getAttribute('comment'); }
    set comment(val) { this.setAttribute('comment', val); this.update(); }
    get state() { return parseInt(this.getAttribute('state')); }
    set state(val) { this.setAttribute('state', val); this.update(); }
    get category() { return this.getAttribute('category'); }
    set category(val) { this.setAttribute('category', val); }

    is_unchecked() { return this.state === 0; }
    hide() { this.style.display = "none"; }
    show() { this.style.display = ""; }

    constructor() { super(); }

    update() {
        let label = this.shadowRoot.getElementById('label');
        label.innerText = this.label;
        let box = this.shadowRoot.getElementById('check');
        box.checked = this.state;
    }

    connectedCallback() {
        let tmpl = document.getElementById('item-template');
        let shadowRoot = this.attachShadow({mode: 'open'});
        let clone = tmpl.content.cloneNode(true);
        shadowRoot.appendChild(clone);
        let label = shadowRoot.getElementById('label');
        label.innerText = this.label;
        let box = shadowRoot.getElementById('check');
        box.checked = this.state;

        let self = this;
        label.addEventListener('click', e => {
            self.shadowRoot.getElementById("container").classList.add("processing");
            let op = "uncheck";
            if (this.is_unchecked()) {
                op = "check";
            }
            let req = new XMLHttpRequest();
            req.open('PUT', `itm/${this.category}/${this.label}/${op}`, true);
            req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            req.onload = function() {
                if (this.status == 200) {
                    let json = JSON.parse(this.response);
                    self.state = json.state;
                    self.shadowRoot.getElementById("container").classList.remove("processing");
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
                    catContainer.innerHTML += `<x-item label="${itm.name}" comment="${itm.comment}" state="${itm.state}" category="${cat.short}" />`;
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

    itemList.forEach(item => {
        if (filter) {
            if (item.label.toUpperCase().indexOf(filter) > -1) {
                item.show();
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
    reload_items();
});
