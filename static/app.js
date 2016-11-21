user_name = 'bornofawesomeness';
var api_url = window.location.protocol + '//' + window.location.hostname + '/retrieve';
var app = new Vue({
    el: '#app',
    data: {
        playlists: {}
    },
    methods: {
      remove: function () {
        this.playlists[0].splice(this.randomIndex(), 1);
      },
      randomIndex: function () {
        return Math.floor(Math.random() * this.playlists[0].length)
      }
    }
});
uri = '/retrieve?uid=bornofawesomeness&playlists=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14';
$.getJSON(uri).then(function(data) {
    console.log(data);
    Vue.set(app, 'playlists', data.contents)
});
