# Simplified Bequest Allocation Script (Children + Grandchildren)
def compute_bequest_distribution(total_pool, generations, real_growth):
    """
    Compute nominal allocations for children and grandchildren using a PV-adjusted rule.
    Reference age is automatically set as the average age of the first generation.
    """
    # Step 0: Compute average age and number of members for each generation
    for gen in generations:
        gen['avg_age'] = sum(gen['ages']) / len(gen['ages'])
        gen['num'] = len(gen['ages'])

    # Step 1: Set reference age as average age of first generation (children)
    reference_age = generations[0]['avg_age']

    # Step 2: Compute discount factor for each generation
    for gen in generations:
        delta_years = reference_age - gen['avg_age']
        gen['discount_factor'] = (1 + real_growth) ** (-delta_years)

    # Step 3: Compute weighted units
    total_weight = sum(gen['num'] * gen['discount_factor'] for gen in generations)
    unit_value = total_pool / total_weight

    # Step 4: Compute nominal allocation per individual
    allocation = {}
    for gen in generations:
        allocation[gen['name']] = [unit_value * gen['discount_factor']] * gen['num']

    return allocation, reference_age


# ===============================
# Interactive input
# ===============================
if __name__ == "__main__":
    total_pool = float(input("Enter total bequest pool (in $): "))
    real_growth = float(input("Enter expected real growth rate (as decimal, e.g., 0.07 for 7%): "))

    num_generations = int(input("Enter number of generations (children + grandchildren only): "))
    generations = []

    for i in range(1, num_generations + 1):
        gen_name = input(f"\nEnter name of generation {i} (e.g., Children, Grandchildren): ")
        ages_str = input(f"Enter ages of all members in {gen_name}, comma-separated: ")
        ages = [float(a.strip()) for a in ages_str.split(",")]
        generations.append({
            "name": gen_name,
            "ages": ages
        })

    allocation, reference_age = compute_bequest_distribution(total_pool, generations, real_growth)

    print(f"\nReference age (average age of first generation): {reference_age:.1f}")
    print("\nNominal bequest allocations per individual:")
    for gen_name, shares in allocation.items():
        for i, amount in enumerate(shares, 1):
            print(f"{gen_name} {i}: ${amount:,.0f}")
