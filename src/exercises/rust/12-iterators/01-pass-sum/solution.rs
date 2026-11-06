use std::io::Read;

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let total: i32 = input
        .split_whitespace()
        .map(|text| text.parse::<i32>().unwrap())
        .filter(|score| *score >= 70)
        .sum();
    println!("{total}");
}
