# fancyiter

It's a thin wrapper around a regular Python iterable that adds additional functionality
and user-friendliness. For complex iteration-based operations this class may offer a more
readble, robust, and maintainable representation than the standard Python approach.

Some of the main features of this package:
* Chainable Rust-style, declarative iteration
* Lazy evaluation/iteration
* Wide variety of iteration operations
* Useable with error-prone iterables for robust error handling & retrying

## Examples

There's a ton of things FancyIter can be used for. Here are a handful of examples to show the basic usage. Note that multi-line expressions need to be wrapped in parenthesis, but they have been omitted here to avoid distraction.

Transform values by applying a function `f(A) -> B` to each value. Collect the result in a new list.

```py
from fancyiter import fancyiter

>>> fancyiter([1, 2, 3])
      .map(lambda x: x + 1)
      .collect()
[2, 3, 4]
```

Reduce the iterator to a single value by repeatedly applying an operation `f(A1, A2) -> B`
```py
>>> fancyiter([1, 2, 3]).reduce(lambda x, y: x + y)
6
```

Check if any elements satisfy a predicate.
```py
>>> arr = [1, 0, 2, 9, 3, 8, 4, 7, 5, 6]
>>> if fancyiter(arr).any(lambda x: x == 5):
      print("welp, there's a 5")
welp, there's a 5

```

Do a lot of weird stuff that doesn't seem particularly useful to chain together.
```py
>>> data = [(1, 2, 3, 4), (5, 6)]
>>> fancyiter(data)
      .flatten()                       # --> [1, 2, 3, 4, 5, 6]
      .windows(3)                      # --> [(1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6)]
      .filter(lambda x: 1 < x[0] < 4)  # --> [(2, 3, 4), (3, 4, 5)]
      .skip(1)                         # --> [(3, 4, 5)]
      .flatten()                       # --> [3, 4, 5]
      .take_while(lambda x: x < 5)     # --> [3, 4]
      .insert(0, 8)                    # --> [8, 3, 4]
      .enumerate()                     # --> [(0, 8), (1, 3), (2, 4)]
      .for_each(
          lambda x:
            print(f"Element #{x[0]+1} = {x[1]}")
      )
Element #1 = 8
Element #2 = 3
Element #3 = 4
```

## As a Combined Data Collection and Processing Pipeline

FancyIter can be used for some pretty nifty things. Here is an example where it is used for greatly-simplified data collection and inline processing.

```py
def _data_reader_impl(n_bytes: int) -> bytes:
    """Some function that reads data, perhaps from a socket, and raises TimeoutError on timeout."""
    ...


def _get_data(chunk_size: int, attempts: int = 5, timeout: float=0.2) -> Generator[bytes]:
    """Returns a generator that continually attempts to read data, and gives up after 5 failures."""
    while True:
        for _ in range(attempts):
            try:
                # recall: yield keyword turns this into a generator with lazy evaluation
                yield _data_reader_impl(n_bytes, timeout)
                break
            except TimeoutError:
                continue
        else:
            raise TimeoutError(f"Read failed: timed out {attempts} times")


def create_pipeline(magic_seq: bytes):
    """Creates the initial data collection/processing pipeline. This can be used elsewhere in your
    code to incorporate different processing methods as needed.
    """
    return fancyiter(_get_data(128)) 
        .skip_while(lambda x: x[:4] != magic_seq)   # 1. skip data until the special sequence is found
        .take(16)                                   # 2. take the following 16 packets, each with 128 bytes
        .flatten()                                  # 3. combine all the packets into one flat collection of bytes
    

def run_processing(output_queue, magic_seq: bytes):
    """Here, we take the output from the pipeline and combine pairs of bytes into 16-bit (short) values.
    """
    create_pipeline(magic_seq)
        .chunks(2)                                  # 4. take the bytes by twos
        .map(lambda b: (b[0] << 8) | b[1])          # 5. combine each byte pair into a short
        .collect_into(output_queue)                 # 6. drop everything into the output queue
```

It's important to note a few things about how `run_processing` works here.
* it reads the bare minimum that is needed; there are no surplus readings
* the steps shown aren't run line-by-line -- all steps are applied as the values are read. In other words, the next packet is read only when the last value of the previous packet has been dropped into the output queue.
* if a timeout error occurs it doesn't lose any data previously processed, since it's all processed and dumped into the output queue before the next packet is read.


The function below is an equivalent implementation of the `run_processing` function using the typical functional approach. Notice how much more explicit the logic is, how much less readable it is, how much more error-prone it could be, and how much less maintainable it could be. Modifying the behavior of the function even slightly could open up the doors to bugs, especially for more complex procedures.
```py
def run_processing2(output_queue, magic_seq: bytes):
    while _get_data(128)[:4] != magic_seq:
        pass

    for _ in range(16):
        data = get_data(128)
        for i in range(0, len(data), 2):
            b1, b2 = data[i], data[i + 1]
            short = (b1[0] << 8) | b2[1]
            output_queue.append(short)
```

It is important to note that `run_processing` is NOT equivalent to the function below. It may be somewhat more efficient, but it has the disadvantage that if a `TimeoutError` occurs at any point, *all* of the processed data is lost.
```py
def WRONG(output_queue, magic_seq: bytes):
    while _get_data(128)[:4] != magic_seq:
        pass
    
    data = [_get_data(128) for _ in range(16)]
    flattened = b''.join(data)
    chunks = [(flattened[i], flattened[i + 1]) for i in range(0, len(flattened), 2)]
    shorts = [(c[0] << 8) | c[1] for c in chunks]
    output_queue.extend(shorts)
```

If losing already-processed data is desired, then it can be done very easily with the FancyIter approach:

```py
def run_processing3(output_queue, magic_seq: bytes):
    temp = create_pipeline(magic_seq)
        .chunks(2)
        .map(lambda b: (b[0] << 8) | b[1])
        .collect()  # here we execute the entire the pipeline to completion first

    output_queue.extend(temp)
```



## License

Apparently I've licensed this under the MIT license.
