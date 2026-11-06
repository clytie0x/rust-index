use std::io::BufRead;

fn main() {
    let mut line = String::new();
    std::io::stdin().lock().read_line(&mut line).unwrap();
    let text = line.trim();
    println!("{text}");
    println!("{text}");
}
