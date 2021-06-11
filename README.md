# Arbitrage
Project idea was to check, if graphs could be used to find arbitrage opportunities in FX markets. For now, only data used is provided by https://exchangerate.host/ . Exchange rates API is a simple and lightweight free service for current and historical foreign exchange rates, however some pairs are rounded and practical usecases don't exist with this data. However for testing purposes this data is sufficient, and can detect arbitrage opportunities in rounded exhange rates. In future hooking up real exchange could be interesting, and provides usecase for multigraphs and maxinum flow algorithm. For example Coinbase provides realtime exchange rate API data, giving chance to try this approach on cryptocurrencies.

The idea in graph based arbitrage is to find maxinum path from one currency back to itself. For example, rates between EUR and Angolan kwanza(AOA), AOA and Vietnamese đồng(VND) could be misspriced, creating path EUR -> AOA -> VND -> EUR. In order to check this, we can transform currencies into nodes and exchange rates to edges between these nodes, where weight of an edge is exchange rate:

![arbitrage_1](https://user-images.githubusercontent.com/78072757/121692728-0bcea600-cad1-11eb-8217-8335aefea16e.png)

We first start from EUR node, with distance 1. We exchange it into AOA with rate of 781. There could also be exchange fees/comissions. For the sake of simplicity, in here we set it to 2.5%. In reality, fees could be included in spreads between buy and sell or be flat, depending on exchange. Exchanging EUR to AOA leaves us with 1 x 781 x 0,985 = 769,4032

![arbitrage_3](https://user-images.githubusercontent.com/78072757/121696124-6a495380-cad4-11eb-8e5c-9705ba7ccf92.png)

We save the distance of first path EUR -> AOA (769,4032) onto the node, so we can for example later check if EUR -> USD -> AOA gives us better results. We move forward, and exchange to VND, leaving us with 769,4032 x 35,74 x 0,985 = 27085,993

![arbitrage_4](https://user-images.githubusercontent.com/78072757/121696288-982e9800-cad4-11eb-893a-2cf1fd937f21.png)

We save the value of 28085,993 onto the VND node, and do last exchange to EUR:
27085,993 x 0,000036 x 0,985 = 0,96047 leaving us with a loss. Because there is no arbitrage in EUR -> AOA -> VND -> EUR, we wont save this path. However, path distances are saved onto the nodes. 

![arbitrage_5](https://user-images.githubusercontent.com/78072757/121701622-c367b600-cad9-11eb-8233-ea2f7afcaa7e.png)

Next if we check EUR -> USD -> AOA, and at AOA notice that path is worse than EUR -> AOA , we stop executing algorithm and move forward. 
path (EUR -> USD -> AOA):
1 x 1.22 x 0,985 x 642,00 x 0,985 = 759,919 < 769,4032
= [EUR -> USD -> AOA] is worse than [EUR -> AOA], no point moving forward

## Next steps (not included yet)
In reality, there may be many different market orders for a swap from first currency to the next. Someone might be willing to trade 1000 euros to dollars at a price of 1.22, and next order might be another 1000 euros at 1.19. As an simple example, if we want to exchange 2000 euros from EUR to USD, we might get better results for only executing the 1.22 trade and transfering last 1000 euros through other currency, like EUR -> AOA -> USD. 

When we include order sizes, we are dealing with multigraphs and maxinum flow problem: What is the best route to flow money from EUR to USD with current market orders, when we account for order size and value?

To test this out, crypto currency exchanges like Coinbase seem to provide free orderbook data on cryptocurrencies.
