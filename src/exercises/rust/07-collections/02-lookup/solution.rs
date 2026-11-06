use std::collections::HashMap;
use std::io::Read;

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let mut lines = input.lines();
    let n: usize = lines.next().unwrap().trim().parse().unwrap();
    let mut scores = HashMap::new();
    for _ in 0..n {
        let line = lines.next().unwrap();
        let mut parts = line.split_whitespace();
        let name = parts.next().unwrap().to_string();
        let score: i32 = parts.next().unwrap().parse().unwrap();
        scores.insert(name, score);
    }
    let query = lines.next().unwrap().trim();
    match scores.get(query) {
        Some(score) => println!("{score}"),
        None => println!("missing"),
    }
}
