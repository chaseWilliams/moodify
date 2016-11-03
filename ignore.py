import numpy as np
import pandas as pd
from lib.spotify import Spotify

user = Spotify(' BQC4oeD8uXz8BCqquQ3yeejiK583XghbpQly58Stjb-PrEo97Ssk5i9lrJYsFP12qtqDJsq3kfyTuf2VaVxppRX743XGswpK71evecsT872OYiiIKn2xnEKOnqiwqsVMhvpGrA-dCwFMf3FL4SZQHTz6v42p6qxktcqKhlHQKsKVcvmloJC_pnxt338k9bWQtcba4i95Sox0')
artist_ids = pd.Series(user.artists).to_frame()
print(artist_ids)
#print(user.get_genres())

arr = np.array([[1, 2, 3],[4, 5, 6]])
def foo(a):
    return a + 1

new_foo = np.vectorize(foo)

#print(new_foo(arr))

class Bar:

    def foo(self, arr):
        def test(a):
            return a + 1
        new_test = np.vectorize(test)
        return new_test(arr)

obj = Bar()
print(obj.foo(arr))