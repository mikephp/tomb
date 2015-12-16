//
//  HintCell.m
//  YGYTPlayer
//
//  Created by dirlt on 15/11/24.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import "HintCell.h"

@interface HintCell()
@property (nonatomic, weak) IBOutlet UILabel *hintLabel;
@end

@implementation HintCell

static HintCell *instance = nil;
+ (id) getInstance {
    if (instance) return instance;
    NSArray *nibs = [[NSBundle mainBundle] loadNibNamed:@"HintCell" owner:nil options:nil];
    instance = nibs[0];
    instance.selectionStyle = UITableViewCellSelectionStyleNone;
    return instance;
}

- (void) setHintText:(NSString *)text {
    self.hintLabel.text = text;
    [self.hintLabel setNeedsDisplay];
}

- (void)awakeFromNib {
    // Initialization code
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];

    // Configure the view for the selected state
}

@end
