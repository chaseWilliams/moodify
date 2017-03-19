console.log(user_name)
default_args = {
    method: 'filter_by',
    by_args: [0.85, false],
    range_args: [0, 100]
}
make_default = function() {
    return JSON.parse(JSON.stringify(default_args))
}
var app = new Vue({
    el: '#app',
    data: {
        filters: [
            {name: 'timeslice', selected: false, argtype: 'year-season', args: {year: 2016, season: 'winter'}},
            {name: 'tags', selected: false, argtype: 'list', args: ''},
            {name: 'count', selected: false, argtype: 'norm', args: make_default()},
            {name: 'popularity', selected: false, argtype: 'norm', args: make_default()},
            {name: 'danceability', selected: false, argtype: 'norm', args: make_default()},
            {name: 'energy', selected: false, argtype: 'norm', args: make_default()},
            {name: 'acousticness', selected: false, argtype: 'norm', args: make_default()},
            {name: 'valence', selected: false, argtype: 'norm', args: make_default()},
            {name: 'tempo', selected: false, argtype: 'norm', args: make_default()}
        ],
        playlist: [],
        identifier: '',
        playlist_name: 'Name your playlist',
        message: '',
        create_failed: false
    },
    methods: {
        create_submission: function() {
            len = this.filters.length
            formatted_filters = {}
            for (i = 0; i < len; i ++) {
                filter = this.filters[i]
                key = filter.name
                if (filter.selected) {
                    if (filter.argtype == 'norm') {
                        if (filter.args.method == 'filter_by') {
                            value = ['filter_by', {
                                percentage: filter.args.by_args[0],
                                reverse: filter.args.by_args[1]
                            }]
                        }
                        else if (filter.args.method == 'filter_in_range') {
                            value = ['filter_in_range', {
                                start: filter.args.range_args[0],
                                stop: filter.args.range_args[1]
                            }]
                        }
                    }
                    else if (filter.argtype == 'list') {
                        value = filter.args.split(',')
                    }
                    else if (filter.argtype == 'year-season') {
                        value = [filter.args.year, filter.args.season]
                    }
                }
                else {
                    value = null
                }
                formatted_filters[key] = value
            }
            return formatted_filters
        },
        create_playlist: function() {
            data = {
                filters: this.create_submission(),
                uid: user_name
            }
            data = JSON.stringify(data)
            self = this
            $.ajax({
                type: 'POST',
                url: '/create',
                headers: {'Content-Type': 'application/json'},
                dataType: 'json',
                data: data
            }).done(function(data) {
                if (data.success) {
                    self.playlist = JSON.parse(data.playlist)
                    self.playlist_id = data.identifier
                    self.message = data.message
                    self.create_failed = false
                }
                else {
                    self.playlist = []
                    self.playlist_id = ''
                    self.message = data.message
                    self.create_failed = true
                }
            })
        },
        save_playlist: function() {
            save_data = {
                identifier: this.playlist_id,
                uid: user_name,
                name: this.playlist_name
            }
            save_data = JSON.stringify(save_data)
            $.ajax({
                type: 'POST',
                url: '/save',
                headers: {'Content-Type': 'application/json'},
                dataType: 'json',
                data: save_data
            }).done(function(data) {
                console.log('successfully saved')
            })
        }
    }
});
