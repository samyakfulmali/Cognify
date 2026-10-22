import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "questions.json"

# Explicit remediation texts naming the exact mistake and the correct method for each misconception
REMEDIATION_MAP = {
    # Fractions Basics
    "inverted_numerator_denominator": (
        "You inverted the numerator and denominator. The numerator represents the counted parts, "
        "while the denominator represents the total equal parts that make up the whole."
    ),
    "ratio_part_to_remaining_part": (
        "You compared the selected parts to the remaining parts rather than the whole. "
        "A fraction must compare the selected parts to the total number of equal parts."
    ),
    "counted_unshaded_as_target": (
        "You counted the remaining or unshaded parts instead of the target parts. "
        "Carefully check which portion the question asks you to measure."
    ),
    "confused_numerator_and_denominator": (
        "You confused the numerator with the denominator. Remember: the denominator on the bottom "
        "shows the total equal partitions, while the numerator on top counts how many parts are taken."
    ),
    "treated_fraction_as_multiplication": (
        "You treated the denominator as a multiplier. The denominator tells you how many equal "
        "pieces the whole is split into, not a value to multiply by."
    ),
    "unit_fraction_confusion": (
        "You selected the unit fraction (1 part) instead of the entire whole. When all parts are "
        "selected, the numerator equals the denominator (e.g., 6/6 = 1 whole)."
    ),
    "zero_whole_confusion": (
        "You assumed 0 whole units instead of 1 complete unit. When all partitioned parts are present, "
        "the fraction equals 1 whole, not 0."
    ),
    "ignored_equal_parts_requirement": (
        "You counted sections without checking if they are equal. Standard fractions require all "
        "partitions of the whole to be exactly equal in size."
    ),
    "spatial_orientation_bias": (
        "You based the fraction on location or visual direction rather than equal portion size. "
        "Fraction values depend strictly on equal part quantities, not spatial position."
    ),

    # Equivalent Fractions
    "add_to_both_terms": (
        "You added the same number to both numerator and denominator. To form equivalent fractions, "
        "you must multiply or divide both terms by the same non-zero factor, never add or subtract."
    ),
    "multiplied_only_numerator": (
        "You multiplied only the numerator. To preserve fraction equivalence, you must multiply "
        "both the numerator and the denominator by the exact same non-zero number."
    ),
    "multiplied_only_denominator": (
        "You multiplied only the denominator. Multiplying only the bottom changes the partition size "
        "without scaling the parts; multiply both terms equally."
    ),
    "incomplete_simplification": (
        "You simplified partially but did not reduce to lowest terms. Divide both numerator and "
        "denominator by their greatest common factor until no common factors remain."
    ),
    "subtracted_from_both_terms": (
        "You subtracted numbers from both terms. Equivalence is created through multiplicative scaling, "
        "never by subtracting values from the top and bottom."
    ),
    "larger_numbers_mean_greater_value": (
        "You assumed larger numerals mean a greater value. In fractions, value is determined by the "
        "ratio of parts to whole; proportional ratios represent equal values."
    ),
    "denominator_determines_value_exclusively": (
        "You judged fraction value solely by the denominator. You must evaluate the ratio between "
        "both the numerator and denominator to determine equivalence."
    ),
    "add_difference_between_denominators": (
        "You added the difference between denominators to the numerator. Equivalent fractions require "
        "multiplying both terms by the scale factor, not adding differences."
    ),
    "added_scale_factor_instead_of_multiplying": (
        "You added the scale factor instead of multiplying. Multiply both numerator and denominator "
        "by the multiplier to generate equivalent fractions."
    ),
    "matched_denominator_to_numerator": (
        "You matched the denominator directly to the numerator. Keep the proportional ratio constant "
        "by applying the exact same multiplier to both terms."
    ),

    # Common Denominators (LCM)
    "confused_gcf_with_lcm": (
        "You picked the GCF. The LCD needs the least common multiple, so list multiples of each "
        "denominator and find the smallest shared one."
    ),
    "multiplied_denominators_instead_of_lcm": (
        "You multiplied the denominators directly instead of finding the Least Common Multiple (LCM). "
        "Listing multiples finds the smallest common denominator, avoiding unnecessarily large numbers."
    ),
    "added_denominators": (
        "You added the denominators together. Common denominators must be a shared multiple of both "
        "numbers, found using LCM rather than addition."
    ),
    "changed_denominator_without_numerator": (
        "You changed the denominator without scaling the numerator. When converting to a common "
        "denominator, multiply the numerator by the same scale factor as the denominator."
    ),
    "added_five_to_numerator": (
        "You added to the numerator instead of multiplying. Multiply the numerator by the scale factor "
        "used to convert the denominator."
    ),
    "matched_numerator_to_original_denominator": (
        "You replaced the numerator with the old denominator. Calculate the new numerator by "
        "multiplying the original numerator by the scaling factor."
    ),
    "addition_of_fractions_disallowed": (
        "You thought fractions cannot be added. Fractions can be added once they share a common "
        "denominator representing identical partition sizes."
    ),
    "fraction_sum_limit_bias": (
        "You assumed fraction sums cannot exceed 1. Adding fractions can yield sums greater than 1, "
        "expressed as improper fractions or mixed numbers."
    ),
    "add_denominators_directly": (
        "You added the denominators directly. When adding fractions, find a common denominator first, "
        "keep that denominator, and only add the numerators."
    ),

    # Fraction Addition & Subtraction
    "multiplied_numerators_and_denominators": (
        "You multiplied the terms instead of adding. Keep the common denominator the same and add only "
        "the numerators across the top."
    ),
    "ignored_first_numerator": (
        "You omitted the first numerator from the sum. Combine all numerators over the shared "
        "common denominator."
    ),
    "multiplied_instead_of_added": (
        "You multiplied the numerators instead of adding them. The plus sign means you combine "
        "numerator quantities, keeping the denominator constant."
    ),
    "added_numerators_multiplied_denominators": (
        "You added the numerators but multiplied the denominators. When fractions already share a "
        "common denominator, the denominator remains unchanged in the answer."
    ),
    "subtracted_denominators_to_zero": (
        "You subtracted the denominators to get zero. The common denominator identifies the part size; "
        "keep it unchanged and subtract only the numerators."
    ),
    "added_denominators_during_subtraction": (
        "You added the denominators during a subtraction problem. Denominators stay the same when "
        "subtracting like fractions; subtract only the numerators."
    ),
    "added_instead_of_subtracted": (
        "You added the numerators instead of subtracting. Pay close attention to the operation sign "
        "and subtract the second numerator from the first."
    ),
    "subtracted_straight_across": (
        "You subtracted unlike denominators straight across. You must first find a common denominator "
        "before subtracting fractional numerators."
    ),
    "subtracted_numerators_without_converting": (
        "You subtracted numerators without converting to a common denominator. Convert both fractions "
        "to a common denominator before combining numerators."
    ),

    # Fraction Multiplication
    "cross_multiplied_instead_of_across": (
        "You cross-multiplied instead of multiplying across. To multiply fractions, multiply straight "
        "across: numerator times numerator, and denominator times denominator."
    ),
    "added_numerators_and_denominators": (
        "You added the terms instead of multiplying. In fraction multiplication, compute the product "
        "of the numerators over the product of the denominators."
    ),
    "cross_multiplied_and_added": (
        "You cross-multiplied and added the products. Simply multiply straight across: top times top, "
        "and bottom times bottom."
    ),
    "multiplied_whole_by_both_terms": (
        "You multiplied both the numerator and denominator by the whole number. Treat the whole number "
        "as a fraction over 1 (e.g., n/1) and multiply only the numerator."
    ),
    "added_whole_to_numerator": (
        "You added the whole number to the numerator. Multiplication scales quantities; multiply the whole "
        "number by the numerator instead of adding."
    ),
    "multiplied_whole_only_by_denominator": (
        "You multiplied the whole number by the denominator. Whole numbers multiply the top numerator; "
        "the denominator remains unchanged when multiplied by an integer."
    ),
    "applied_addition_rules_to_multiplication": (
        "You looked for common denominators. Multiplication does not require common denominators; multiply "
        "straight across (top × top, bottom × bottom)."
    ),
    "arbitrary_rule_generalization": (
        "You applied an invalid arithmetic shortcut. Stick to the core rule: multiply numerators together "
        "and denominators together directly."
    ),
    "hybrid_addition_multiplication_confusion": (
        "You mixed addition and multiplication procedures. Only addition and subtraction require common "
        "denominators; multiplication works straight across."
    ),

    # Fraction Division & Reciprocals
    "multiplied_without_inverting": (
        "You multiplied without taking the reciprocal of the divisor. Use keep-change-flip: keep the first "
        "fraction, change division to multiplication, and flip the second fraction."
    ),
    "flipped_dividend_not_divisor": (
        "You inverted the first fraction instead of the second. Always keep the first fraction (dividend) "
        "unchanged and invert only the second fraction (divisor)."
    ),
    "added_inverted_fractions": (
        "You added the fractions after flipping. Dividing fractions transforms into multiplication by "
        "the reciprocal, not addition."
    ),
    "confused_reciprocal_with_opposite": (
        "You took the negative opposite instead of the reciprocal. The reciprocal flips the numerator "
        "and denominator without changing the sign."
    ),
    "opposite_and_reciprocal_merged": (
        "You flipped the fraction AND changed its sign. A standard reciprocal only swaps the numerator "
        "and denominator; keep the original sign."
    ),
    "doubled_terms_instead_of_reciprocal": (
        "You doubled the numbers instead of inverting. To find the reciprocal, swap the numerator "
        "and denominator positions."
    ),
    "multiplied_by_whole_number": (
        "You multiplied by the whole number instead of its reciprocal. When dividing by a whole number n, "
        "multiply by its reciprocal 1/n."
    ),
    "inverted_first_fraction_and_multiplied": (
        "You flipped the first fraction instead of the divisor. Keep the first fraction as-is and invert "
        "the fraction you are dividing by."
    ),
    "added_terms": (
        "You added the numbers instead of multiplying by the reciprocal. Division is performed by multiplying "
        "by the flipped divisor."
    ),

    # Negative Numbers & Integers
    "subtracted_instead_of_multiplied": (
        "You subtracted instead of multiplying. The operation calls for multiplication; compute the product of the terms."
    ),
    "multiplied_instead_of_subtracted": (
        "You multiplied instead of subtracting. Pay attention to the minus operation symbol and subtract the terms."
    ),
    "two_negatives_make_positive_in_addition": (
        "You applied the multiplication sign rule to addition. When adding two negative numbers, add their "
        "magnitudes and keep the negative sign (e.g., -a + -b = -(a+b))."
    ),
    "subtracted_magnitudes_instead_of_accumulating": (
        "You subtracted the numbers instead of accumulating debt. Adding two negatives moves further left "
        "on the number line, summing their values with a negative sign."
    ),
    "subtracted_magnitudes_and_dropped_negative": (
        "You subtracted magnitudes and dropped the negative sign. Sum the magnitudes and keep the negative "
        "sign when adding numbers with identical negative signs."
    ),
    "subtracted_directly_ignoring_double_negative": (
        "You treated subtracting a negative as regular subtraction. Subtracting a negative is equivalent "
        "to adding a positive (a - (-b) = a + b)."
    ),
    "subtracted_to_negative_sum": (
        "You incorrectly evaluated the double negative. Remember that subtracting a negative number "
        "increases the value by turning into addition."
    ),
    "subtracted_positive_values": (
        "You subtracted instead of adding. Two minus signs together (- -) cancel out to become a positive plus sign."
    ),
    "negative_times_negative_is_negative": (
        "You concluded that a negative times a negative is negative. The product of two numbers with "
        "matching negative signs is always positive."
    ),
    "added_instead_of_multiplied": (
        "You added the integers instead of multiplying them. Pay attention to parentheses indicating "
        "multiplication and multiply the values."
    ),
    "added_absolute_values": (
        "You added the absolute values without multiplying. Evaluate the product first, then apply the "
        "sign rule (negative × negative = positive)."
    ),
    "dropped_negative_sign_in_division": (
        "You dropped the negative sign during division. Dividing numbers with different signs (positive ÷ negative) "
        "always produces a negative quotient."
    ),
    "subtracted_instead_of_divided": (
        "You subtracted instead of dividing. Perform the division operation between the values and "
        "determine the resulting sign."
    ),
    "multiplied_instead_of_divided": (
        "You multiplied the values instead of dividing. Divide the dividend by the divisor and apply the "
        "rule that opposite signs yield a negative result."
    ),

    # Order of Operations (PEMDAS)
    "evaluated_left_to_right_without_precedence": (
        "You evaluated from left to right without precedence. Follow PEMDAS: evaluate Parentheses and "
        "Exponents, then Multiplication and Division, before Addition and Subtraction."
    ),
    "multiplied_everything": (
        "You multiplied all numbers together. Perform operations in sequence according to PEMDAS, "
        "executing multiplication before performing addition."
    ),
    "added_four_and_two_first": (
        "You added before multiplying. Under PEMDAS, multiplication must be computed before addition."
    ),
    "multiplied_base_by_exponent": (
        "You multiplied the base by the exponent (e.g., 2 × 2). An exponent means multiplying the base "
        "by itself that many times (e.g., 2² = 2 × 2, 3² = 3 × 3 = 9)."
    ),
    "ignored_parentheses_applied_exponent_to_two": (
        "You applied the exponent before resolving the expression inside parentheses. Always evaluate "
        "operations inside parentheses first."
    ),
    "added_before_squaring": (
        "You added before evaluating the exponent. Exponents take precedence over addition; compute "
        "powers before adding terms outside."
    ),
    "added_two_and_three_before_division": (
        "You added before dividing. Division takes precedence over addition; perform division first."
    ),
    "subtracted_three_at_the_end": (
        "You grouped terms out of order. Complete division and multiplication first from left to right, "
        "then compute addition and subtraction."
    ),
    "prioritized_multiplication_over_division": (
        "You performed multiplication before division. Multiplication and division share equal precedence; "
        "evaluate them in order from left to right as they appear."
    ),
    "divided_result_by_four": (
        "You altered the order of operations. Evaluate multiplication and division strictly from left "
        "to right when they share equal priority."
    ),

    # Variables & Expressions
    "concatenated_digits_instead_of_multiplying": (
        "You placed digits side by side instead of multiplying. A coefficient next to a variable (like 3x) "
        "means 3 multiplied by x, not concatenation."
    ),
    "added_three_and_seven_then_multiplied": (
        "You added the coefficient and constant before substituting. Multiply the coefficient by the "
        "variable value first, then add the constant."
    ),
    "added_variable_value_directly": (
        "You added the variable value instead of multiplying by its coefficient. Compute coefficient × variable "
        "before performing subsequent additions."
    ),
    "treated_subtraction_of_negative_as_subtraction": (
        "You subtracted the negative variable without converting signs. Subtracting a negative variable creates "
        "an addition step (e.g., 4 - (-3) = 4 + 3)."
    ),
    "overall_sign_inversion": (
        "You inverted the overall expression sign. Substitute the value with parentheses and simplify each term "
        "following standard sign rules."
    ),
    "ignored_coefficients": (
        "You ignored the coefficient preceding the variable. Multiply the variable by its coefficient "
        "before combining with constants."
    ),
    "reversed_subtraction_order_in_word_problem": (
        "You reversed the subtraction order. Phrases like 'less than a number' mean subtracting from the "
        "variable (e.g., '5 less than x' translates to x - 5, not 5 - x)."
    ),
    "applied_grouping_prematurely": (
        "You grouped with parentheses inappropriately. Translate words step-by-step according to algebraic "
        "precedence."
    ),
    "confused_twice_with_half": (
        "You divided instead of multiplying. 'Twice a number' means multiplying the number by 2."
    ),
    "squared_without_parentheses_giving_negative": (
        "You assumed (-x)² is negative. When a negative number is squared inside parentheses, negative × negative "
        "produces a positive result."
    ),
    "sign_error_on_second_term": (
        "You miscalculated the sign on the substituted term. Carefully track signs during substitution and "
        "multiplication."
    ),
    "dropped_negative_sign_in_both_terms": (
        "You dropped negative signs during evaluation. Maintain negative signs when substituting and follow "
        "integer multiplication rules."
    ),

    # Combining Like Terms
    "combined_unlike_terms_variables_and_constants": (
        "You combined variable terms with constant terms. Only like terms (terms with the exact same variable "
        "and exponent) can be combined together."
    ),
    "added_coefficients_ignoring_subtraction_sign": (
        "You ignored the subtraction sign preceding the term. Treat the minus sign as a negative coefficient "
        "when combining like terms."
    ),
    "changed_exponent_when_adding_terms": (
        "You added exponents while adding like terms. When adding like terms, add only the numerical coefficients; "
        "the variable and its exponent remain unchanged."
    ),
    "combined_different_variable_terms": (
        "You combined terms containing different variables. Terms with different variables (like x and y) are "
        "unlike terms and cannot be combined."
    ),
    "sign_error_on_subtraction_term": (
        "You misapplied the sign of the subtracted term. The minus sign in front of a term belongs to its coefficient."
    ),
    "added_negative_magnitudes_incorrectly": (
        "You made an arithmetic error when combining signed coefficients. Combine coefficients as integers on a number line."
    ),
    "confused_multiplication_exponent_rules_with_addition": (
        "You applied multiplication exponent rules to addition. Exponents only change when multiplying terms; "
        "adding like terms keeps the exponent identical."
    ),
    "ignored_higher_degree_exponent": (
        "You combined terms with different powers. Terms like x and x² have different degrees and cannot be "
        "added together."
    ),
    "multiplied_terms_instead_of_leaving_uncombined": (
        "You multiplied unlike terms together instead of keeping them separate. When simplifying a polynomial sum, "
        "unlike terms must remain separate."
    ),
    "failed_to_distribute_negative_sign_to_second_term": (
        "You did not distribute the negative sign to the second term inside parentheses. Distribute the minus "
        "sign to every term within the parentheses."
    ),
    "added_instead_of_subtracting_variable": (
        "You added the variable term instead of subtracting it. Check the operational sign preceding the term "
        "before combining coefficients."
    ),

    # Distributive Property
    "distributed_only_to_first_term": (
        "You distributed only to the first term. The distributive property requires you to multiply the outside "
        "factor by EVERY term inside the parentheses (a(b + c) = ab + ac)."
    ),
    "combined_terms_inside_parentheses_improperly": (
        "You combined unlike terms inside parentheses. You cannot add a variable term and a constant; you must "
        "distribute the outside factor to each term."
    ),
    "multiplied_sum_by_power": (
        "You introduced an improper exponent. Distribute the scalar factor across the terms without changing "
        "variable powers."
    ),
    "sign_error_distributing_negative_to_negative": (
        "You made a sign error distributing a negative to a negative term. Multiplying a negative factor by a "
        "negative term produces a positive product."
    ),
    "dropped_first_negative_sign": (
        "You dropped the negative sign on the outside factor. Multiply both terms inside by the full negative factor."
    ),
    "added_before_distributing": (
        "You added terms before distributing. Multiplication distributes over addition; perform distributive "
        "multiplication before adding outside constants."
    ),
    "forgot_to_add_the_external_constant": (
        "You distributed correctly but forgot to combine the outside constant term. Complete the simplification "
        "by adding all constant terms together."
    ),
    "ignored_negative_outside_parentheses": (
        "You ignored the negative sign outside the parentheses. A negative sign preceding parentheses acts as "
        "-1, inverting the sign of every term inside."
    ),
    "flipped_both_signs_to_positive": (
        "You converted both terms to positive. Distribute the negative sign carefully: each term flips to its "
        "opposite sign."
    ),

    # One-Step Equations (Add/Sub)
    "added_instead_of_subtracted": (
        "You added instead of using the inverse operation. To eliminate an added constant, subtract that same "
        "amount from both sides of the equation."
    ),
    "subtracted_fifteen_from_seven": (
        "You subtracted in the reverse order. Subtract the constant from the side containing the variable from "
        "the other side (e.g., x + a = b means x = b - a)."
    ),
    "subtracted_nine_from_both_sides": (
        "You subtracted when you needed to add. The inverse of subtracting 9 is adding 9 to both sides."
    ),
    "sign_error_on_addition_with_negatives": (
        "You made an arithmetic sign error when adding to a negative integer. Add carefully using number line rules."
    ),
    "dropped_negative_sign_on_negative_four": (
        "You dropped the negative sign on the result. When adding opposite signed numbers, the sign of the number "
        "with greater absolute value determines the result sign."
    ),
    "subtracted_twelve_instead_of_adding": (
        "You subtracted instead of adding. The inverse of subtracting 12 is adding 12 to both sides of the equation."
    ),
    "subtracted_five_from_twelve": (
        "You applied the operation inconsistently across sides. Add the constant to both sides to maintain balance."
    ),
    "sign_inversion_error": (
        "You inverted the sign of the solution incorrectly. Balance the equation step-by-step preserving correct signs."
    ),
    "applied_same_operation_instead_of_inverse": (
        "You repeated the same operation instead of the inverse. To isolate the variable, always apply the opposite "
        "operation to both sides."
    ),
    "confused_additive_and_multiplicative_inverses": (
        "You confused addition with multiplication inverses. Use addition or subtraction to cancel constant terms."
    ),
    "violated_equation_balance_rule": (
        "You modified only one side of the equation. Whatever operation you apply to one side must be applied "
        "identically to the opposite side."
    ),

    # One-Step Equations (Mult/Div)
    "multiplied_instead_of_divided": (
        "You multiplied instead of dividing. To undo multiplication by a coefficient, divide both sides by that coefficient."
    ),
    "subtracted_coefficient_instead_of_dividing": (
        "You subtracted the coefficient. When a coefficient multiplies a variable (e.g., 4x), use division to isolate the variable."
    ),
    "added_coefficient": (
        "You added the coefficient. Coefficients multiply variables; use division to undo multiplication."
    ),
    "divided_instead_of_multiplied": (
        "You divided instead of multiplying. To undo division (e.g., x/4 = 7), multiply both sides by the denominator."
    ),
    "added_four_instead_of_multiplying": (
        "You added instead of multiplying. The variable is divided by 4; undo division by multiplying both sides by 4."
    ),
    "subtracted_four": (
        "You subtracted the denominator. Undo division by multiplying both sides of the equation by that denominator."
    ),
    "forgot_negative_coefficient_sign": (
        "You forgot to divide by the negative sign. Divide both sides by the full negative coefficient (-n) to ensure "
        "the variable is positive."
    ),
    "added_five_instead_of_dividing": (
        "You added instead of dividing. Coefficients multiply variables; divide both sides by the negative coefficient."
    ),
    "multiplied_by_fraction_without_reciprocal": (
        "You multiplied by the fractional coefficient directly. To isolate the variable, multiply both sides by the "
        "reciprocal of the fractional coefficient."
    ),
    "inverted_fraction_division_step": (
        "You made an inversion error. Multiply both sides by the flipped reciprocal of the fraction."
    ),
    "multiplied_by_denominator_only": (
        "You multiplied by only the denominator without dividing by the numerator. Multiply by the complete reciprocal (b/a)."
    ),

    # Two-Step Equations
    "added_five_instead_of_subtracting": (
        "You added the constant instead of subtracting it. First isolate the variable term by subtracting the added "
        "constant from both sides."
    ),
    "divided_before_subtracting_constant": (
        "You divided before isolating the variable term. Standard two-step order is to undo addition/subtraction "
        "first, then undo multiplication/division."
    ),
    "subtracted_five_but_forgot_to_divide": (
        "You subtracted the constant but forgot to divide by the coefficient. Finish solving by dividing both sides "
        "by the variable's coefficient."
    ),
    "subtracted_seven_instead_of_adding": (
        "You subtracted instead of adding. The equation has -7; undo subtraction by adding 7 to both sides first."
    ),
    "double_sign_inversion_error": (
        "You made multiple sign errors during inverse operations. Track negative signs carefully at each isolation step."
    ),
    "divided_after_subtracting_instead_of_multiplying": (
        "You divided instead of multiplying by the denominator. Undo division by multiplying both sides by the denominator."
    ),
    "multiplied_ten_by_three_and_subtracted_four": (
        "You multiplied before undoing the constant. Add or subtract the standalone constant before multiplying by the denominator."
    ),
    "added_four_to_ten_then_multiplied": (
        "You performed operations out of order. Add or subtract the constant term first, then multiply across by the denominator."
    ),
    "divided_constant_without_distributing_to_all_terms": (
        "You divided without distributing across all terms. Undo addition/subtraction first to avoid fractional complications."
    ),
    "confused_operations_order": (
        "You confused the order of inverse operations. Follow reverse PEMDAS: undo addition/subtraction first, then multiplication/division."
    ),

    # Multi-Step Equations
    "added_variable_terms_across_equals": (
        "You added variable terms across the equals sign. To move a variable term to the other side, apply the inverse operation (subtract it)."
    ),
    "added_three_and_fifteen": (
        "You added constants on the same side incorrectly. Combine like terms with their proper operational signs."
    ),
    "subtracted_six_from_ten_instead_of_adding": (
        "You subtracted instead of adding to isolate constants. Apply the opposite operation to move constants across the equals sign."
    ),
    "added_variables_instead_of_subtracting": (
        "You added variable terms across the equals sign instead of subtracting. Collect all variable terms onto one side using inverse operations."
    ),
    "sign_error_distributing_negative": (
        "You made a sign error distributing the negative coefficient. Distribute the negative sign to all terms inside before combining."
    ),
    "forgot_to_add_distributed_constant": (
        "You forgot to combine the distributed constant with existing constants. Combine all constant terms on each side before isolating."
    ),
    "subtracted_constant_incorrectly": (
        "You made an arithmetic error when moving constants. Use balance operations carefully on both sides."
    ),
    "dropped_multipliers": (
        "You dropped a coefficient multiplier. Distribute and balance terms systematically without omitting factors."
    ),

    # Linear Inequalities
    "forgot_to_flip_inequality_sign": (
        "You didn't flip the inequality sign. Crucial rule: whenever you multiply or divide both sides of an "
        "inequality by a negative number, the inequality sign must flip direction."
    ),
    "sign_error_on_division_result": (
        "You made a sign error in the division step. Check that dividing positive by negative yields a negative value, "
        "and remember to flip the inequality sign."
    ),
    "dropped_both_negative_and_sign_flip": (
        "You dropped both the negative sign and the required inequality flip. Dividing by a negative flips the sign "
        "and produces a negative quotient."
    ),
    "flipped_inequality_when_not_dividing_by_negative": (
        "You flipped the inequality sign when dividing by a positive number. Only flip the inequality sign when "
        "multiplying or dividing by a negative number."
    ),
    "subtracted_three_instead_of_adding": (
        "You subtracted when you needed to add to isolate terms. Add 3 to both sides first, then divide by the coefficient."
    ),
    "flipped_sign_on_subtraction": (
        "You flipped the inequality sign during subtraction. Subtracting or adding numbers never flips the inequality sign; "
        "it only flips when multiplying or dividing by a negative."
    ),
    "confused_right_hand_sign_with_divisor_sign": (
        "You decided to flip based on the constant's sign rather than the divisor's sign. The inequality sign ONLY flips "
        "if the number you are multiplying or dividing BY is negative."
    ),
}

def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    updated_count = 0
    missing = []

    for q in questions:
        for opt in q.get("options", []):
            misc = opt.get("misconception")
            if misc:
                remediation = REMEDIATION_MAP.get(misc)
                if not remediation:
                    # Generic high-quality fallback for any unmapped
                    readable = misc.replace("_", " ")
                    remediation = (
                        f"You made an error with {readable}. Identify where the operation diverged and apply "
                        f"the correct mathematical procedure to reach {q['explanation']}."
                    )
                    missing.append(misc)
                opt["remediation"] = remediation
                updated_count += 1
            else:
                opt["remediation"] = None

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2)

    print(f"Updated {updated_count} options in questions.json with specific remediation texts.")
    if missing:
        print(f"Missing mapped items ({len(set(missing))}): {set(missing)}")
    else:
        print("100% of misconceptions were explicitly mapped!")

if __name__ == "__main__":
    main()
