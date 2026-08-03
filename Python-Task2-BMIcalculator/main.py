def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)
    return bmi

def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal Weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obesity"

def main():
    print("===== BMI Calculator =====")

    try:
        weight = float(input("Enter your weight (kg): "))
        height = float(input("Enter your height (cm): "))

        if weight <= 0 or height <= 0:
            print("Height and weight must be greater than 0.")
            return

        bmi = calculate_bmi(weight, height)

        print(f"\nYour BMI: {bmi:.2f}")
        print("Category:", bmi_category(bmi))

    except ValueError:
        print("Please enter valid numeric values.")

if __name__ == "__main__":
    main()