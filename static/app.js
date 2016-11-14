user_name = 'bornofawesomeness';
var api_url = window.location.protocol + '//' + window.location.hostname + '/retrieve'
var app = new Vue({
    el: '#app',
    computed: {
        playlists: function() {
            console.log('starting')
            response = $.get('/retrieve?uid=bornofawesomeness&playlists=7').then(function(data) {
                console.log('ay');
                return data['contents'];
            }.bind(this));
            console.log(response);
            return response;
        }
    }
});
