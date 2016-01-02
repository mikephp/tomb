//
//  ViewController.h
//  ThirdIdTest
//
//  Created by dirlt on 15/12/4.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <Google/SignIn.h>
#import <FBSDKCoreKit/FBSDKCoreKit.h>
#import <FBSDKLoginKit/FBSDKLoginKit.h>

@interface ViewController : UIViewController<GIDSignInUIDelegate, FBSDKLoginButtonDelegate>
@property (nonatomic, weak) IBOutlet GIDSignInButton* signInButton;
@property (nonatomic, weak) IBOutlet UIButton *signOutButton;
@property (nonatomic, weak) IBOutlet FBSDKLoginButton* fbButton;

@end

