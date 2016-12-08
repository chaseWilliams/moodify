user_name = 'bornofawesomeness';
var api_url = window.location.protocol + '//' + window.location.hostname + '/retrieve';
var app = new Vue({
    el: '#app',
    data: {
        playlists: [],
        shortened_playlists: [],
        display_playlists: [],
        playlist_names: [],
        show_all: false,
        curr_playlist_index: 0
    },
    methods: {
        // acts as initialization method
        substantiate_shortened_playlists: function () {
            new_playlists = this.playlists.slice(0);
            for (i = 0; i < 15; i ++) {
                new_playlists[i] = this.playlists[i].slice(0, 5);
            }
            this.$set(this, 'shortened_playlists', new_playlists);
            this.$set(this, 'display_playlists', this.shortened_playlists.slice(0, 3));
            this.initialize_playlist_names();
        },
        switch_show_all: function() {
          if (this.show_all) {
            this.$set(this, 'display_playlists', this.shortened_playlists.slice(this.curr_playlist_index, this.curr_playlist_index + 3));
            this.$set(this, 'show_all', false);
          } else {
            this.$set(this, 'display_playlists', this.playlists.slice(this.curr_playlist_index, this.curr_playlist_index + 3));
            this.$set(this, 'show_all', true);
          }
        },
        increment_display_playlists: function() {
            if (this.curr_playlist_index < 12) {
                index = this.curr_playlist_index;
                this.$set(this, 'curr_playlist_index', index + 3);
                if (this.show_all) {
                    this.$set(this, 'display_playlists', this.playlists.slice(index + 3, index + 6));
                } else {
                    this.$set(this, 'display_playlists', this.shortened_playlists.slice(index + 3, index + 6));
                    console.log('set new arr');
                }
            }
        },
        decrement_display_playlists: function() {
          if (this.curr_playlist_index > 0) {
            index = this.curr_playlist_index;
            this.$set(this, 'curr_playlist_index', index - 3);
            if (this.show_all) {
              this.$set(this, 'display_playlists', this.playlists.slice(index - 3, index));
            } else {
              this.$set(this, 'display_playlists', this.shortened_playlists.slice(index - 3, index));
            }
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
            console.log('saving playlist ' + playlist);
        }
    }
});



uri = '/retrieve?uid=bornofawesomeness&playlists=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14';
$.getJSON(uri).then(function(data) {
    Vue.set(app, 'playlists', data.contents);
    app.substantiate_shortened_playlists();
});
