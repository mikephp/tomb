//
//  PlayListVC.m
//  YGYTPlayer
//
//  Created by dirlt on 15/11/12.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import "PlayListVC.h"
#import "PlayListCell.h"
#import "VideoVC.h"
#import "RemoteDataSource.h"
#import "SearchVC.h"
#import "HintCell.h"
#import <MJRefresh/MJRefresh.h>

@interface PlayListVC ()
@property (nonatomic, strong) UIBarButtonItem *rightButton;
@end

@implementation PlayListVC

- (void)viewDidLoad {
    [super viewDidLoad];
    
    // RemoteDataSource *rds = [RemoteDataSource getInstance];
    self.languages = @[@"ALL", @"Yoga", @"ヨガ", @"Ioga", @"瑜伽", @"йога"];
    NSArray* locales = @[@"", @"en", @"ja", @"pt", @"zh", @"ru"];
    NSString *langId = [[[NSLocale preferredLanguages] objectAtIndex:0] substringToIndex:2];
    // NSLog(@"language id = %@", langId);
    [locales enumerateObjectsUsingBlock:^(id  _Nonnull obj, NSUInteger idx, BOOL * _Nonnull stop) {
        if ([obj isEqualToString:langId]) {
            self.langIdx = idx;
            *stop = YES;
        }
    }];
    self.langIdx = 0;
    [PlayListCell configureTableView:self.tableView];
    self.rightButton = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemSearch target:self action:@selector(didSearchButtonTapped:)];
    MJRefreshNormalHeader *header = [MJRefreshNormalHeader headerWithRefreshingTarget:self refreshingAction:@selector(refreshData)];
    [header setTitle:@"Pull down to refresh" forState:MJRefreshStateIdle];
    [header setTitle:@"Release to refresh" forState:MJRefreshStatePulling];
    [header setTitle:@"Loading ..." forState:MJRefreshStateRefreshing];
    header.stateLabel.font = [UIFont systemFontOfSize:15];
    header.stateLabel.textColor = [UIColor blueColor];
    header.lastUpdatedTimeLabel.hidden = YES;
    self.tableView.mj_header = header;
    MJRefreshAutoNormalFooter *footer = [MJRefreshAutoNormalFooter footerWithRefreshingTarget:self refreshingAction:@selector(fetchData)];
    [footer setTitle:@"Click or drag up to refresh" forState:MJRefreshStateIdle];
    [footer setTitle:@"Loading more ..." forState:MJRefreshStateRefreshing];
    [footer setTitle:@"No more data" forState:MJRefreshStateNoMoreData];
    footer.stateLabel.font = [UIFont systemFontOfSize:15];
    footer.stateLabel.textColor = [UIColor blueColor];
    self.tableView.mj_footer = footer;
    [self refresh];
}

- (void) refreshData {
    [self clearData];
    [self fetchData];
}
- (void) refresh {
    [self.tableView.mj_header beginRefreshing];
}

- (void) clearData {
    self.data = [[NSMutableArray alloc] init];
    self.eof = NO;
    [self.tableView reloadData];
}

- (void) fetchData {
    RemoteDataSource *rds = [RemoteDataSource getInstance];
    static const int DEFAULT_FETCH_COUNT = 20;
    NSString *sid = @"";
    if (self.data.count) sid = self.data[self.data.count-1][@"sid"];
    NSString* key = [NSString stringWithFormat:@"index/?v=2&s=%d&sid=%@&c=%d&lang=%d&q=%@", self.data.count, sid, DEFAULT_FETCH_COUNT, self.langIdx, self.query];
    key = [key stringByAddingPercentEncodingWithAllowedCharacters:[NSCharacterSet URLQueryAllowedCharacterSet]];
    // set loading view.
    __weak PlayListVC *me = self;
    [rds fetchDataWithoutCache:key withComplete:^(NSString *key, NSDictionary *json) {
        if (json) {
            // NSLog(@"fetch data complete. key = %@, json = %@", key, json);
            // NSLog(@"fetch data complete. key = %@, json = (ignored)", key);
            NSArray *vds = (NSArray*)json[@"vds"];
            if (vds.count < DEFAULT_FETCH_COUNT) {
                me.eof = YES;
            }
            [me.data addObjectsFromArray: vds];
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            if (me.eof) {
                [me.tableView.mj_footer endRefreshingWithNoMoreData];
            } else {
                [me.tableView.mj_footer endRefreshing];
            }
            [me.tableView.mj_header endRefreshing];
            [me.tableView reloadData];
        });
    }];
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
    self.parentViewController.navigationItem.title = @"PLAYLIST";
    self.parentViewController.navigationItem.rightBarButtonItem = self.rightButton;
}

- (void) didSearchButtonTapped: (id)sender {
    // NSLog(@"search button tapped...");
    SearchVC* vc = [SearchVC getInstance];
    [vc loadData:self];
    [self.navigationController pushViewController:vc animated:YES];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
// #warning Incomplete implementation, return the number of sections
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
// #warning Incomplete implementation, return the number of rows
    // if (self.data.count == 0) return 1;
    return self.data.count;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    if (self.data.count == 0) {
        HintCell *cell = [HintCell getInstance];
        [cell setHintText:@"Not Found"];
        return cell;
    }
    PlayListCell *cell = [PlayListCell fetchCell:self.tableView];
    NSDictionary *json = self.data[indexPath.row];
    [cell fillWithDictionary:json withCellKind:CELL_KIND_PLAYLIST];
    return cell;
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    VideoVC *vc = [VideoVC getInstance];
    [vc loadData:self.data[indexPath.row]];
    [self.navigationController pushViewController:vc animated:YES];
}

//- (void)tableView:(UITableView *)tableView willDisplayCell:(UITableViewCell *)cell forRowAtIndexPath:(NSIndexPath *)indexPath {
//    if (self.eof || indexPath.row != (self.data.count - 1)) return;
//
//    //NSLog(@"will display trailing cell");
//    [self fetchData];
//}

/*
// Override to support conditional editing of the table view.
- (BOOL)tableView:(UITableView *)tableView canEditRowAtIndexPath:(NSIndexPath *)indexPath {
    // Return NO if you do not want the specified item to be editable.
    return YES;
}
*/

/*
// Override to support editing the table view.
- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath {
    if (editingStyle == UITableViewCellEditingStyleDelete) {
        // Delete the row from the data source
        [tableView deleteRowsAtIndexPaths:@[indexPath] withRowAnimation:UITableViewRowAnimationFade];
    } else if (editingStyle == UITableViewCellEditingStyleInsert) {
        // Create a new instance of the appropriate class, insert it into the array, and add a new row to the table view
    }   
}
*/

/*
// Override to support rearranging the table view.
- (void)tableView:(UITableView *)tableView moveRowAtIndexPath:(NSIndexPath *)fromIndexPath toIndexPath:(NSIndexPath *)toIndexPath {
}
*/

/*
// Override to support conditional rearranging of the table view.
- (BOOL)tableView:(UITableView *)tableView canMoveRowAtIndexPath:(NSIndexPath *)indexPath {
    // Return NO if you do not want the item to be re-orderable.
    return YES;
}
*/

/*
#pragma mark - Navigation

// In a storyboard-based application, you will often want to do a little preparation before navigation
- (void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender {
    // Get the new view controller using [segue destinationViewController].
    // Pass the selected object to the new view controller.
}
*/

@end
