use std::io::BufRead;

fn max_score(a: i32, b: i32) -> i32 {
    if a > b { a } else { b }
}

fn main() {
    let mut line = String::new();
    std::io::stdin().lock().read_line(&mut line).unwrap();
    let mut parts = line.split_whitespace();
    let a: i32 = parts.next().unwrap().parse().unwrap();
    let b: i32 = parts.next().unwrap().parse().unwrap();
    println!("{}", max_score(a, b));
}
