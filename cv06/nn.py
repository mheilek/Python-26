import math

def signiod(x):
    return 1 / (1 + math.exp(-x))


def neuron_network(
    has_four_legs,
    has_fur,
    has_eyes,
    has_tail,
    has_ears,
    has_nose,
    has_fins
):
    dog = (has_four_legs * 0.4 + 
           has_fur * 0.1 + 
           has_tail * 0.3 +
           has_eyes * 0.4 +
           has_nose * 0.1 +
           has_ears * 0.5 + 
           has_fins * -0.2
        ) + 0.1 #bias
    
    fish = (has_four_legs * -0.2 + 
           has_fur * -0.2 + 
           has_tail * 0.1 +
           has_eyes * 0.1 +
           has_nose * 0.1 +
           has_ears * 0.1 +
           has_fins * 0.6
        ) + 0.6
    cat = (has_four_legs * 0.4 + 
           has_fur * 0.3 + 
           has_tail * 0.5 +
           has_eyes * 0.5 +
           has_nose * 0.5 +
           has_ears * 0.3 + 
           has_fins * 0.8
        ) + 0.1 
    return {signiod(dog), signiod(fish), signiod(cat)}
    
def do_softmax(items):
    total_signoid = sum(items)
    for index, i in enumerate(items):
        print(f"{index } - > {i / total_signoid}")
    
    
if __name__ == "__main__":
    do_softmax(neuron_network(
        has_four_legs=0.75,
        has_fur= 1,
        has_eyes= 1,
        has_ears= 1,
        has_nose=1,
        has_fins=0,
        has_tail=1   
    ))
    