use std::io::Read;

fn verdict(score: i32) -> &'static str {
    if score >= 70 { "pass" } else { "fail" }
}

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let score: i32 = input.trim().parse().unwrap();
    assert!(verdict(70) == "pass");
    println!("{}", verdict(score));
}
