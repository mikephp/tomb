//
//  ViewController.m
//  GPTest
//
//  Created by dirlt on 15/12/4.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import "ViewController.h"

@interface ViewController ()

@end

@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view, typically from a nib.
    [GIDSignIn sharedInstance].uiDelegate = self;
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (IBAction)didTapSignOut:(id)sender {
    NSLog(@"trigger sign out");
    [[GIDSignIn sharedInstance] disconnect];
}

@end
