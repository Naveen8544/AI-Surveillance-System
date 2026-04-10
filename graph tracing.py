def get_output(value):
    
    mapping = {
        (0, 0): "+ -",
        (0, 1): "- -",
        (1, 0): "- +",
        (1, 1): "+ +"
    }

    return mapping.get(value, "Invalid input")


#  Input
try:
    user_input = tuple(map(int, input("Enter (e.g. 0 1): ").split()))

    result = get_output(user_input)

    print("Output:", result)

except:
    print("❌ Invalid format! Use like: 0 1")