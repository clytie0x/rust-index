use std::io::BufRead;

fn main() {
    let mut line = String::new();
    std::io::stdin().lock().read_line(&mut line).unwrap();
    let mut parts = line.split_whitespace();
    let math: i32 = parts.next().unwrap().parse().unwrap();
    let science: i32 = parts.next().unwrap().parse().unwrap();
    println!("{}", math + science);
}
