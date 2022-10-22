# ccxws

CCXWS – CryptoCurrency eXchange Websocket Library

### For Developers

## requirement

1. python >= `3.10`
1. Formatter
    1. black
    1. isort
1. linter
    1. flake8
    1. mypy
    1. pysen

## How to develop

1. coding
2. `python test_bitfinex.py`
3. `pysen run format`

## event emmition

### public

#### update_orderbook

```python
{
    'event': 'update_orderbook',
    'symbol': symbol,
    'data': orderbook.to_dict()
}
```

#### update_execution

```python
{
    'event': 'update_execution',
    'symbol': symbol,
    'data': execution.to_dict(symbol)
}
```

### private

#### update_user_execution

```python
{
    'event': 'update_user_execution',
    'symbol': symbol,
    'data': user_execution.to_dict(symbol)
}
```