//
//  FilterVC.m
//  YGYTPlayer
//
//  Created by dirlt on 15/11/13.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import "SearchVC.h"
#import "RemoteDataSource.h"
#import "SearchLangCell.h"

@interface SearchVC()
@property (nonatomic, strong) UISearchController *searchController;
@property (nonatomic, strong) NSMutableArray *searchHistory;
@property (nonatomic, strong) NSArray *popularTerms;
@property (nonatomic, strong) NSMutableArray *suggestedTerms;
@end

@implementation SearchVC

static SearchVC *instance = nil;
+ (id) getInstance {
    if (instance) return instance;
    UIStoryboard* sb = [UIStoryboard storyboardWithName:@"Main" bundle:[NSBundle mainBundle]];
    instance = (SearchVC*)[sb instantiateViewControllerWithIdentifier:@"SearchVC"];
    instance.searchController = [[UISearchController alloc] initWithSearchResultsController:nil];
    instance.searchController.searchBar.delegate = instance;
    instance.searchController.searchResultsUpdater = instance;
    return instance;
}

- (void)viewDidLayoutSubviews {
    [self.searchController.searchBar sizeToFit];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view.
    // self.navigationItem.title = @"SEARCH";
    // self.navigationItem.titleView = self.searchController.searchBar;
    self.tableView.tableHeaderView = self.searchController.searchBar;
    self.searchController.hidesNavigationBarDuringPresentation = YES;
    self.searchController.dimsBackgroundDuringPresentation = NO;
    self.definesPresentationContext = YES;
    [self.searchController.searchBar sizeToFit];
    // 隐藏left bar button item.
//    self.navigationItem.leftBarButtonItem = nil;
//    self.navigationItem.hidesBackButton = YES;
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
    // self.searchController.searchBar.showsCancelButton = YES;
    RemoteDataSource *rds = [RemoteDataSource getInstance];
    __weak SearchVC *me = self;
    [rds fetchData:@"pop/" withExpireInterval:800 withComplete:^(NSString *key, NSDictionary *json) {
        if (!json) return ;
        me.popularTerms = (NSArray*) json[@"terms"];
        [me.tableView reloadData];
    }];
    [rds loadSearchHistory:10 withComplete:^(NSMutableArray *array) {
        me.searchHistory = array;
        [me.tableView reloadData];
        // [self.searchController.searchBar sizeToFit];
    }];
    SearchLangCell *cell = [SearchLangCell getInstance];
    [cell.sc setSelectedSegmentIndex:self.rootVC.langIdx];
}

- (void) loadData:(PlayListVC *)rootVC {
    self.rootVC = rootVC;
    self.languages = rootVC.languages;
    SearchLangCell *cell = [SearchLangCell getInstance];
    [cell fillLanguages:self.languages];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

//- (void)searchBarCancelButtonClicked:(UISearchBar *)searchBar {
//    [self.navigationController popViewControllerAnimated:YES];
//}

- (void)searchBarSearchButtonClicked:(UISearchBar *)searchBar {
    [self goSearch:searchBar.text];
}

- (void)goSearch: (NSString*) term {
    self.rootVC.langIdx = [SearchLangCell getInstance].sc.selectedSegmentIndex;
    self.rootVC.query = term;
    if (self.rootVC.query.length) {
        RemoteDataSource *rds = [RemoteDataSource getInstance];
        [rds saveSearchHistory:self.rootVC.query];
    }
    [self.rootVC refresh];
    [self.navigationController popViewControllerAnimated:YES];
}

- (void)updateHints: (UISearchController*) searchController {
    NSLog(@"update search. text = %@, scope bar = %d", searchController.searchBar.text, searchController.searchBar.selectedScopeButtonIndex);
}

- (void)updateSearchResultsForSearchController:(UISearchController *)searchController {
    [self updateHints:searchController];
}
- (void)searchBar:(UISearchBar *)searchBar selectedScopeButtonIndexDidChange:(NSInteger)selectedScope {
    [self updateHints:self.searchController];
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    if (self.suggestedTerms) {
        return 1; // just suggested terms
    } else {
        return 3; // language + history + popular terms.
    }
}
- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    if (self.suggestedTerms) {
        return self.suggestedTerms.count;
    } else {
        switch(section) {
            case 0: return 1;
            case 1: return self.popularTerms.count;
            case 2: return self.searchHistory.count;
            default: return 0;
        }
    }
}
- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    if (indexPath.section == 0) return [SearchLangCell getInstance];
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:@"SearchResultCell" forIndexPath:indexPath];
    if (self.suggestedTerms) {
        cell.textLabel.text = self.suggestedTerms[indexPath.row];
    } else if(indexPath.section == 1) {
        cell.textLabel.text = self.popularTerms[indexPath.row];
    } else if (indexPath.section == 2) {
        cell.textLabel.text = self.searchHistory[indexPath.row];
    }
    return cell;
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section {
    if (!self.suggestedTerms) {
        switch (section) {
            case 0: return nil;
            case 1: return @"Popular";
            case 2: return @"History";
            default: return nil;
        }
    }
    return nil;
}

- (BOOL)tableView:(UITableView *)tableView canEditRowAtIndexPath:(NSIndexPath *)indexPath {
    if (self.suggestedTerms || indexPath.section != 2) return NO;
    return YES;
}

// Override to support editing the table view.
- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath {
    if (editingStyle == UITableViewCellEditingStyleDelete) {
        RemoteDataSource *rds = [RemoteDataSource getInstance];
        [rds removeSearchHistory:self.searchHistory[indexPath.row]];
        [self.searchHistory removeObjectAtIndex:indexPath.row];
        [self.tableView reloadData];
    }
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    NSString *term = nil;
    if (self.suggestedTerms) {
        term = self.suggestedTerms[indexPath.row];
    } else if(indexPath.section == 1) {
        term = self.popularTerms[indexPath.row];
    } else if (indexPath.section == 2) {
        term = self.searchHistory[indexPath.row];
    }
    if (term) {
        [self goSearch:term];
    }
}

/*
#pragma mark - Navigation

// In a storyboard-based application, you will often want to do a little preparation before navigation
- (void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender {
    // Get the new view controller using [segue destinationViewController].
    // Pass the selected object to the new view controller.
}
*/

@end
