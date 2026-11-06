use std::io::Read;

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let word = input.trim();
    match word {
        "pass" => println!("ok"),
        "fail" => println!("no"),
        _ => println!("unknown"),
    }
}
