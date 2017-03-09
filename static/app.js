console.log(user_name)
var api_url = window.location.protocol + '//' + window.location.hostname + '/retrieve';
var app = new Vue({
    el: '#app',
    data: {
        filters: [],
        message: 'hello'
    },
    methods: {
        
    }
});



uri = '/retrieve?uid=' + user_name + '&playlists=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14';
//$.getJSON(uri).then(function(data) {
    //Vue.set(app, 'playlists', data.contents);
    //app.substantiate_shortened_playlists();
//});
