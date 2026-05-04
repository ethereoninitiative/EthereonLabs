from recursive_reflection_layer_r1 import RecursiveReflectionLayer


def run_sea_trial():
    layer = RecursiveReflectionLayer()

    test_input = "stabilize luminous threads in the chamber"

    receipt = layer.reflect(
        test_input,
        mode="Observation",
        constraints=["no_overclaim"],
    )

    print("INPUT:", test_input)
    print("REFLECTION RECEIPT:")
    for k, v in receipt.to_dict().items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    run_sea_trial()
