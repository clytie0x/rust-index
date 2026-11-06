use std::io::Read;

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let mut nums = input.split_whitespace();
    let n: usize = nums.next().unwrap().parse().unwrap();
    let mut scores = Vec::new();
    for _ in 0..n {
        let x: i32 = nums.next().unwrap().parse().unwrap();
        scores.push(x);
    }
    let boxed = Box::new(scores);
    let mut total = 0;
    for score in boxed.iter() {
        total += score;
    }
    println!("{total}");
}
