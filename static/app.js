user_name = 'bornofawesomeness';
var api_url = window.location.protocol + '//' + window.location.hostname + '/retrieve';
var app = new Vue({
    el: '#app',
    data: {
        playlists: [],
        shortened_playlists: [],
        display_playlists: [],
        playlist_names: [],
        show_all: false
    },
    methods: {
        // acts as initialization method
        substantiate_shortened_playlists: function () {
            new_playlists = this.playlists.slice(0);
            for (i = 0; i < 15; i ++) {
                new_playlists[i] = this.playlists[i].slice(0, 5);
            }
            this.$set(this, 'shortened_playlists', new_playlists);
            this.$set(this, 'display_playlists', this.shortened_playlists);
            this.initialize_playlist_names();
        },
        switch_display_playlist: function() {
          if (this.show_all) {
            this.$set(this, 'display_playlists', this.shortened_playlists);
            this.$set(this, 'show_all', false);
          } else {
            this.$set(this, 'display_playlists', this.playlists);
            this.$set(this, 'show_all', true);
          }
        },
        initialize_playlist_names: function() {
            arr = [];
            for (i = 0; i < 15; i ++) {
                arr[i] = i + '';
            }
            this.$set(this, 'playlist_names', arr);
        },
        save_playlist: function(playlist) {
            data = {
                playlist: playlist,
                uid: user_name,
                name: 'Moodify# ' + playlist
            };
            data = JSON.stringify(data);
            $.ajax({
                type: 'POST',
                url: '/save',
                headers: {'Content-Type': 'application/json'},
                dataType: 'json',
                data: data
            });
        }
    },
    components: {
        'playlist-list': Playlist_List
    }
});

var Playlist_List = {
    template: ''
};

uri = '/retrieve?uid=bornofawesomeness&playlists=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14';
$.getJSON(uri).then(function(data) {
    Vue.set(app, 'playlists', data.contents);
    app.substantiate_shortened_playlists();
});
