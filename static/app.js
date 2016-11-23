user_name = 'bornofawesomeness';
var api_url = window.location.protocol + '//' + window.location.hostname + '/retrieve';
var app = new Vue({
    el: '#app',
    data: {
        playlists: [],
        shortened_playlists: []
    },
    methods: {
        remove: function () {
            this.playlists[0].splice(this.randomIndex(), 1);
        },
        randomIndex: function () {
            return Math.floor(Math.random() * this.playlists[0].length)
        },
        substantiate_shortened_playlists: function () {
            new_playlists = this.playlists;
            for (i = 0; i < 15; i ++) {
                new_playlists[i] = this.playlists[i].slice(0, 5);
            }
            this.$set(this, 'shortened_playlists', new_playlists);
            this.set_display_playlist();
        },
        set_display_playlist: function() {

        },
        show_all: function() {

        }
    }
});
uri = '/retrieve?uid=bornofawesomeness&playlists=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14';
$.getJSON(uri).then(function(data) {
    Vue.set(app, 'playlists', data.contents);
    app.substantiate_shortened_playlists();
});