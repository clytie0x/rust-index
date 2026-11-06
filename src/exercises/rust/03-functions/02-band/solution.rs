use std::io::BufRead;

fn band(score: i32) -> &'static str {
    if score >= 80 {
        "A"
    } else if score >= 70 {
        "B"
    } else {
        "C"
    }
}

fn main() {
    let mut line = String::new();
    std::io::stdin().lock().read_line(&mut line).unwrap();
    let score: i32 = line.trim().parse().unwrap();
    println!("{}", band(score));
}
