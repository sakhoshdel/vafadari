!function (t) {
    var e = {};

    function n(i) {
        if (e[i]) return e[i].exports;
        var o = e[i] = {i: i, l: !1, exports: {}};
        return t[i].call(o.exports, o, o.exports, n), o.l = !0, o.exports
    }

    n.m = t, n.c = e, n.d = function (t, e, i) {
        n.o(t, e) || Object.defineProperty(t, e, {enumerable: !0, get: i})
    }, n.r = function (t) {
        "undefined" != typeof Symbol && Symbol.toStringTag && Object.defineProperty(t, Symbol.toStringTag, {value: "Module"}), Object.defineProperty(t, "__esModule", {value: !0})
    }, n.t = function (t, e) {
        if (1 & e && (t = n(t)), 8 & e) return t;
        if (4 & e && "object" == typeof t && t && t.__esModule) return t;
        var i = Object.create(null);
        if (n.r(i), Object.defineProperty(i, "default", {
            enumerable: !0,
            value: t
        }), 2 & e && "string" != typeof t) for (var o in t) n.d(i, o, function (e) {
            return t[e]
        }.bind(null, o));
        return i
    }, n.n = function (t) {
        var e = t && t.__esModule ? function () {
            return t.default
        } : function () {
            return t
        };
        return n.d(e, "a", e), e
    }, n.o = function (t, e) {
        return Object.prototype.hasOwnProperty.call(t, e)
    }, n.p = "", n(n.s = 0)
}([function (t, e, n) {
    "use strict";
    n.r(e);
    var i = function () {
            function t(t) {
                var e = this;
                this.listener = function (t) {
                    (t.matches ? e.matchFns : e.unmatchFns).forEach((function (t) {
                        t()
                    }))
                }, this.toggler = window.matchMedia(t), this.toggler.addListener(this.listener), this.matchFns = [], this.unmatchFns = []
            }

            return t.prototype.add = function (t, e) {
                this.matchFns.push(t), this.unmatchFns.push(e), (this.toggler.matches ? t : e)()
            }, t
        }(), o = function (t) {
            return Array.prototype.slice.call(t)
        }, s = function (t, e) {
            return o((e || document).querySelectorAll(t))
        },
        r = ("ontouchstart" in window || navigator.msMaxTouchPoints, navigator.userAgent.indexOf("MSIE") > -1 || navigator.appVersion.indexOf("Trident/") > -1),
        a = "mm-spn", c = function () {
            function t(t, e, n, i, o) {
                this.node = t, this.title = e, this.slidingSubmenus = i, this.selectedClass = n, this.node.classList.add(a), r && (this.slidingSubmenus = !1), this.node.classList.add(a + "--" + o), this.node.classList.add(a + "--" + (this.slidingSubmenus ? "navbar" : "vertical")), this._setSelectedl(), this._initAnchors()
            }

            return Object.defineProperty(t.prototype, "prefix", {
                get: function () {
                    return a
                }, enumerable: !1, configurable: !0
            }), t.prototype.openPanel = function (t) {
                var e = t.parentElement;
                if (this.slidingSubmenus) {
                    var n = t.dataset.mmSpnTitle;
                    e === this.node ? this.node.classList.add(a + "--main") : (this.node.classList.remove(a + "--main"), n || o(e.children).forEach((function (t) {
                        t.matches("a, span") && (n = t.textContent)
                    }))), n || (n = this.title), this.node.dataset.mmSpnTitle = n, s(".mm-spn--open", this.node).forEach((function (t) {
                        t.classList.remove(a + "--open"), t.classList.remove(a + "--parent")
                    })), t.classList.add(a + "--open"), t.classList.remove(a + "--parent");
                    for (var i = t.parentElement.closest("ul"); i;) i.classList.add(a + "--open"), i.classList.add(a + "--parent"), i = i.parentElement.closest("ul")
                } else {
                    var r = t.matches(".mm-spn--open");
                    s(".mm-spn--open", this.node).forEach((function (t) {
                        t.classList.remove(a + "--open")
                    })), t.classList[r ? "remove" : "add"](a + "--open");
                    for (var c = t.parentElement.closest("ul"); c;) c.classList.add(a + "--open"), c = c.parentElement.closest("ul")
                }
            }, t.prototype._setSelectedl = function () {
                var t = s("." + this.selectedClass, this.node), e = t[t.length - 1], n = null;
                e && (n = e.closest("ul")), n || (n = this.node.querySelector("ul")), this.openPanel(n)
            }, t.prototype._initAnchors = function () {
                var t = this;
                this.node.addEventListener("click", (function (e) {
                    var n = e.target, i = !1;
                    (i = (i = (i = i || function (t) {
                        return !!t.matches("a")
                    }(n)) || function (e) {
                        var n;
                        return !!(n = e.closest("span") ? e.parentElement : !!e.closest("li") && e) && (o(n.children).forEach((function (e) {
                            e.matches("ul") && t.openPanel(e)
                        })), !0)
                    }(n)) || function (e) {
                        var n = s(".mm-spn--open", e), i = n[n.length - 1];
                        if (i) {
                            var o = i.parentElement.closest("ul");
                            if (o) return t.openPanel(o), !0
                        }
                        return !1
                    }(n)) && e.stopImmediatePropagation()
                }))
            }, t
        }(), d = function () {
            function t(t, e) {
                var n = this;
                void 0 === t && (t = null), this.wrapper = document.createElement("div"), this.wrapper.classList.add("mm-ocd"), this.wrapper.classList.add("mm-ocd--" + e), this.content = document.createElement("div"), this.content.classList.add("mm-ocd__content"), this.wrapper.append(this.content), this.backdrop = document.createElement("div"), this.backdrop.classList.add("mm-ocd__backdrop"), this.wrapper.append(this.backdrop), document.body.append(this.wrapper), t && this.content.append(t);
                var i = function (t) {
                    n.close(), t.stopImmediatePropagation()
                };
                this.backdrop.addEventListener("touchstart", i, {passive: !0}), this.backdrop.addEventListener("mousedown", i, {passive: !0})
            }

            return Object.defineProperty(t.prototype, "prefix", {
                get: function () {
                    return "mm-ocd"
                }, enumerable: !1, configurable: !0
            }), t.prototype.open = function () {
                this.wrapper.classList.add("mm-ocd--open"), document.body.classList.add("mm-ocd-opened")
            }, t.prototype.close = function () {

                //this two line is where menu is closing
                document.getElementsByClassName('sidemenu-close-btn')[0].style.opacity = 0;
                setTimeout(function (){
                    document.getElementsByClassName('sidemenu-close-btn')[0].style.display = 'none';
                },500);

                this.wrapper.classList.remove("mm-ocd--open"), document.body.classList.remove("mm-ocd-opened")
            }, t
        }(), u = function () {
            function t(t, e) {
                void 0 === e && (e = "all"), this.menu = t, this.toggler = new i(e)
            }

            return t.prototype.navigation = function (t) {
                var e = this;
                if (!this.navigator) {
                    var n = (t = t || {}).title, i = void 0 === n ? "دسته بندی" : n, o = t.selectedClass,
                        s = void 0 === o ? "Selected" : o, r = t.slidingSubmenus, a = void 0 === r || r, d = t.theme,
                        u = void 0 === d ? "light" : d;
                    this.navigator = new c(this.menu, i, s, a, u), this.toggler.add((function () {
                        return e.menu.classList.add(e.navigator.prefix)
                    }), (function () {
                        return e.menu.classList.remove(e.navigator.prefix)
                    }))
                }
                return this.navigator
            }, t.prototype.offcanvas = function (t) {
                var e = this;
                if (!this.drawer) {
                    var n = (t = t || {}).position, i = void 0 === n ? "left" : n;
                    this.drawer = new d(null, i);
                    var o = document.createComment("original menu location");
                    this.menu.after(o), this.toggler.add((function () {
                        e.drawer.content.append(e.menu)
                    }), (function () {
                        e.drawer.close(), o.after(e.menu)
                    }))
                }
                return this.drawer
            }, t
        }();
    e.default = u;
    window.MmenuLight = u
}]);