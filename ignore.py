import numpy as np
import pandas as pd
from lib.spotify import Spotify

user = Spotify(' BQDkOUp_S65z58v-r3l8eoyLZcs0J3s0VGPO5xDLR8INsTddaR3_CS7LKIt_EX7U5bZuw2qt7s0BZUJnLiv7gcPisoPvF9pVsv7pnpiFE8ZeyrfE1hOlQm3Dr2_bDDS8rIAVWnM1i0BBF8_716dJUICNZWXBb3NV6MTNUOjYFH6wHKHD5AUnwWelHhR_ci_NUIbs_tid6RaQ')
df = pd.DataFrame(user.get_genres().split(','))
print(df)
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