use std::io::Read;

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    if let Ok(n) = input.trim().parse::<i32>() {
        println!("score = {n}");
    } else {
        println!("skip");
    }
}
