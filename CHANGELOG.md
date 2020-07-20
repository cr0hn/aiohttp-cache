# 2.1.0 (20 Jul 2020)

## Fixes
- using sha256 from hashlib see
(https://github.com/cr0hn/aiohttp-cache/pull/26)

## Features
- Supports python 3.6, 3.7 and 3.8
- Monthly maintenance update

# 2.0.2 (8 Apr 2020)

## Bug fix
- Fixed #22 when chache wasn't worked if other middlewares
appended

# 2.0.1 (31 Jan 2020)

## Codebase improvements
- Supports python 3.8
- Monthly maintenance update

# 2.0.0 (30 Jan 2020)

## Features:
- Add possibility to setup custom cache key
- Now the key value being encrypted when
written to Redis

## Bug fix
- Use new style aiohttp middlewares

## Codebase improvements
- Use poetry
- Use pre-commit linters
- Add integration tests including real calls
to redis backend
- Use gitlab ci

# 1.0.0 (11 Nov 2016)

- First release
