# Markov Chain Novel Text Generator

An experiment in probabilistic text generation using Markov chains. Using word-level chains for the title and authorship and sentence-level chains for the content. Experimentation with n-gram n values, and training works used, can further tune text coherence, however, shows randomnistic limitations for NLP and generation.

Reads novels, trains Markov chain, generates n works with m words each, user provided, now playing with tuning and expanding Markov model. Current model is essentially a 3-gram textual probability learner learning tests of 25 works in roughly two wall clock seconds.

Novels sourced from public works on [Gutenberg](https://www.gutenberg.org/) using [scrape script](./scrape.py), then [proc script](./proc.py) to pre-process the novels for text training with [gen script](./gen.py).

## License

This work is freely available under the MIT license, see [LICENSE](./LICENSE).
